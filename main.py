import edge_tts
import asyncio
import os
import datetime
import sys
from tqdm import tqdm
from natsort import natsorted

# 配置参数
CONFIG = {
    'output_folder': 'out',
    'input_folder': 'in',
    'voice': 'zh-CN-XiaoxiaoNeural',
    'rate': '+0%',
    'volume': '+0%',
    'batch_size': 10
}

async def text_to_speech(text, voice, rate, volume, output_path):
    """封装语音生成逻辑"""
    try:
        tts = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume
        )
        await tts.save(output_path)
        
        if not os.path.exists(output_path):
            raise ValueError("文件未生成")
        if os.path.getsize(output_path) < 1024:
            raise ValueError("生成文件过小（可能不完整）")
        return True
    except Exception as e:
        raise RuntimeError(f"语音生成失败: {str(e)}") from e

def validate_directories():
    """目录验证与创建"""
    os.makedirs(CONFIG['output_folder'], exist_ok=True)
    if not os.path.exists(CONFIG['input_folder']):
        print(f"\033[31m错误：输入目录 {CONFIG['input_folder']} 不存在\033[0m")
        sys.exit(1)

def get_input_files():
    """获取待处理文件列表"""
    files = [
        f for f in os.listdir(CONFIG['input_folder'])
        if f.endswith('.txt') and not f.startswith('.')
    ]
    if not files:
        print("\033[31m错误：输入目录中没有可处理的txt文件\033[0m")
        sys.exit(1)
    return natsorted(files)

async def process_file(filename, pbar):
    """处理单个文件（返回错误信息）"""
    full_path = os.path.join(CONFIG['input_folder'], filename)
    output_path = os.path.join(
        CONFIG['output_folder'],
        filename.replace(".txt", ".mp3")
    )
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            raise ValueError("空文本内容")
        
        await text_to_speech(
            text,
            CONFIG['voice'],
            CONFIG['rate'],
            CONFIG['volume'],
            output_path
        )
        
        pbar.update(1)
        return (filename, None)
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        return (filename, str(e))

async def get_user_choice(prompt):
    """修复后的异步输入函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

async def batch_processor(file_list, pbar):
    """分批次处理（含错误暂停）"""
    processed_files = []
    total_batches = (len(file_list) + CONFIG['batch_size'] - 1) // CONFIG['batch_size']
    
    for batch_num in range(total_batches):
        start = batch_num * CONFIG['batch_size']
        end = start + CONFIG['batch_size']
        batch_files = file_list[start:end]
        
        # 执行批次处理
        tasks = [process_file(f, pbar) for f in batch_files]
        results = await asyncio.gather(*tasks)
        
        # 检查错误
        errors = [(f, err) for f, err in results if err is not None]
        if errors:
            print("\n\033[31m" + "="*40)
            print(f"批次 {batch_num+1}/{total_batches} 发生错误：")
            for f, err in errors:
                print(f"• {f}: {err}")
            print("="*40 + "\033[0m")
            
            # 获取用户选择（修复await使用）
            choice = (await get_user_choice(
                "请检查错误后选择操作：\n"
                " [C] 继续处理后续批次\n"
                " [R] 重试当前批次\n"
                " [Q] 退出程序\n"
                "请输入选择（C/R/Q）："
            )).lower()
            
            if choice == 'q':
                print("\n\033[33m用户终止程序\033[0m")
                return processed_files
            elif choice == 'r':
                # 重试当前批次
                tasks = [process_file(f, pbar) for f in batch_files]
                retry_results = await asyncio.gather(*tasks)
                processed_files.extend([f for f, _ in retry_results])
            else:
                processed_files.extend([f for f, _ in results])
        else:
            processed_files.extend(batch_files)
            
        # 更新进度描述
        pbar.set_description(f"已处理批次 {batch_num+1}/{total_batches}")
    
    return processed_files

def validate_results(file_list):
    """最终结果验证"""
    success_count = 0
    failed = []
    
    for f in file_list:
        mp3_path = os.path.join(
            CONFIG['output_folder'],
            f.replace(".txt", ".mp3")
        )
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1024:
            success_count += 1
        else:
            failed.append(f)
    
    print("\n\033[36m" + "="*40)
    print(f"最终完成度：{success_count}/{len(file_list)}")
    print("="*40 + "\033[0m")
    
    if failed:
        print("\033[31m以下文件未成功生成：")
        for f in failed:
            print(f" - {f}")
        print("\033[0m")

async def main():
    print("\033[36m" + "="*40)
    print("Novel 2 MP3")
    print("版本:1.5.1")
    print(f"edga_tts版本：edge_tts-{edge_tts.__version__}")
    print("="*40 + "\033[0m")
    print(f"本次工作线程数:{CONFIG['batch_size']}")
    
    validate_directories()
    file_list = get_input_files()
    
    # 用户确认
    confirm = (await get_user_choice(
        f"即将处理 {len(file_list)} 个文件，确认继续？(y/N) "
    )).lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 执行处理
    start_time = datetime.datetime.now()
    with tqdm(total=len(file_list), desc="处理进度", unit="file") as pbar:
        processed = await batch_processor(file_list, pbar)
    
    # 最终验证
    validate_results(file_list)
    
    # 性能统计
    total_time = (datetime.datetime.now() - start_time).total_seconds()
    print(f"\n\033[32m总耗时: {total_time:.2f}秒\033[0m")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[33m用户中断操作\033[0m")