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
    'batch_size': 20
}

async def my_function(text, voice, rate, volume, output):
    """
    使用edge_tts生成语音并保存到指定文件
    :param text: 要转换的文本
    :param voice: 语音类型
    :param rate: 语速
    :param volume: 音量
    :param output: 输出文件路径
    """
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await tts.save(output)

def ensure_directory_exists(directory):
    """
    确保目录存在，如果不存在则创建
    :param directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_input_folder():
    """
    获取输入文件夹路径，如果输入文件夹不存在则提示用户输入
    :return: 输入文件夹路径
    """
    indir = CONFIG['input_folder']
    if not os.path.exists(indir):
        instr = input(f'\033[38;2;255;0;0m输入文件夹{indir}不存在,指定输入文件夹?(Y/n)\033[0m')
        if instr == 'n':
            sys.exit()
        else:
            indir = input('键入输入文件夹: ')
            if not os.path.exists(indir):
                print(f'\033[38;2;255;0;0m输入文件夹{indir}不存在!\033[0m')
                sys.exit()
    return indir

def get_file_count(directory):
    """
    获取目录中文件的数量
    :param directory: 目录路径
    :return: 文件数量
    """
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

async def process_file(indir, filename, voice, rate, volume, pbar):
    """
    处理单个文件，生成语音并更新进度条
    :param indir: 输入文件夹路径
    :param filename: 文件名
    :param voice: 语音类型
    :param rate: 语速
    :param volume: 音量
    :param pbar: 进度条对象
    """
    with open(f'{indir}/{filename}', 'rb') as f:
        data = f.read()
        text = data.decode('utf-8')

    output = f'{CONFIG["output_folder"]}/{filename.replace(".txt", ".mp3")}'
    from_time = datetime.datetime.now()
    
    await my_function(text, voice, rate, volume, output)
    
    to_time = datetime.datetime.now()
    elapsed_time = (to_time - from_time).total_seconds()
    pbar.update(1)
    pbar.set_description(f'{filename} successed TIME: {elapsed_time:.2f}s')

async def main():
    """
    主函数，处理所有文件并记录总运行时间
    """
    ensure_directory_exists(CONFIG['output_folder'])
    indir = get_input_folder()

    form = get_file_count(CONFIG['output_folder'])
    to = get_file_count(indir)

    if to == 0:
        print(f'\033[38;2;255;0;0m输入文件夹{indir}中没有可处理的文件!\033[0m')
        sys.exit()

    file_list = natsorted([f for f in os.listdir(indir) if f.endswith('.txt')])

    if not os.path.exists('.breakpointfile'):
        with open('.breakpointfile', 'w') as f:
            pass

    ingo = input(f'\033[38;2;0;204;255m程序将处理{len(file_list)}个文件,是否继续?(Y/n)\033[0m')
    if ingo == 'n':
        sys.exit()

    start_time = datetime.datetime.now()

    with tqdm(total=len(file_list), desc="Processing", unit="file") as pbar:
        for start in range(0, len(file_list), CONFIG['batch_size']):
            end = min(start + CONFIG['batch_size'], len(file_list))
            tasks = [process_file(indir, file_list[i], CONFIG['voice'], CONFIG['rate'], CONFIG['volume'], pbar) for i in range(start, end)]
            await asyncio.gather(*tasks)

    end_time = datetime.datetime.now()
    total_elapsed_time = end_time - start_time

    print('\033[38;2;0;255;0m总运行时间: {:.2f}秒\033[0m'.format(total_elapsed_time.total_seconds()))

    if os.path.exists(".breakpointfile"):
        os.remove(".breakpointfile")

# 使用asyncio启动主程序
asyncio.run(main())
