import edge_tts
import asyncio
import os
import datetime
import sys

async def my_function(TEXT, voice, rate, volume, output):
    tts = edge_tts.Communicate(text=TEXT, voice=voice, rate=rate, volume=volume)
    await tts.save(output)

output_folder = 'out'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

indir = 'in'
if not os.path.exists(indir):
    instr = input(f'\033[38;2;255;0;0m输入文件夹{indir}不存在,指定输入文件夹?(Y/n)\033[0m')
    if instr == 'n':
        sys.exit()
    else:
        indir = input('键入输入文件夹')
        if not os.path.exists(indir):
            print(f'\033[38;2;255;0;0m输入文件夹{indir}不存在!\033[0m')
            sys.exit()

form = len([name for name in os.listdir('out') if os.path.isfile(os.path.join('out', name))])
to = len([name for name in os.listdir(indir) if os.path.isfile(os.path.join(indir, name))])

if to == 0:
    print(f'\033[38;2;255;0;0m输入文件夹{indir}中没有可处理的文件!\033[0m')
    sys.exit()

padding_length = len(str(to))
iL = form + 1  # 从已处理文件的下一个开始

if not os.path.exists('.breakpointfile'):
    with open('.breakpointfile', 'w') as f:
        pass

ingo = input(f'\033[38;2;0;204;255m程序将从{iL}到{to},是否继续?(Y/n)\033[0m')
if ingo == 'n':
    sys.exit()

voice = 'zh-CN-XiaoxiaoNeural'
rate = '+0%'
volume = '+0%'

async def process_file(indir, i, voice, rate, volume, padding_length):
    j = "{:0{}d}".format(i, padding_length)
    with open(f'{indir}/{j}.txt', 'rb') as f:
        data = f.read()
        TEXT = data.decode('utf-8')

    output = f'out/{j}.mp3'
    from_time = datetime.datetime.now()
    print('\033[38;2;0;204;255m' + f'{j}.txt -> {j}.mp3 TIME: 0.00s' + '\033[0m', end='\r')
    
    await my_function(TEXT, voice, rate, volume, output)
    
    to_time = datetime.datetime.now()
    elapsed_time = (to_time - from_time).total_seconds()
    print('\033[38;2;50;205;50m' + f'{j}.txt successed TIME: {elapsed_time:.2f}s' + '\033[0m')

async def main(indir, iL, to, voice, rate, volume, batch_size=10):
    for start in range(iL, to + 1, batch_size):
        end = min(start + batch_size - 1, to)
        tasks = [process_file(indir, i, voice, rate, volume, padding_length) for i in range(start, end + 1)]
        await asyncio.gather(*tasks)

# 记录程序开始时间
start_time = datetime.datetime.now()

# 使用asyncio启动主程序
asyncio.run(main(indir, iL, to, voice, rate, volume))

# 记录结束时间并计算总运行时间
end_time = datetime.datetime.now()
total_elapsed_time = end_time - start_time

print('\033[38;2;0;255;0m总运行时间: {:.2f}秒\033[0m'.format(total_elapsed_time.total_seconds()))

if os.path.exists(".breakpointfile"):
    os.remove(".breakpointfile")
