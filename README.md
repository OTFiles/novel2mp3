# novel2mp3

这是一个使用 `edge_tts` 库生成语音的 Python 脚本。该脚本能够将指定文件夹中的文本文件转换为语音文件，并保存到输出文件夹中。我经常用它转换小说，所以叫这个名字。

## 主要功能

1. **批量处理文本文件**：脚本能够批量处理指定文件夹中的文本文件，并将每个文本文件转换为语音文件。
2. **异步处理**：使用 `asyncio` 进行异步处理，提高处理效率。
3. **进度条显示**：使用 `tqdm` 库显示处理进度，方便用户了解处理状态。
4. **自定义配置**：用户可以通过配置文件自定义语音类型、语速、音量等参数。

## 配置参数

脚本使用一个 `CONFIG` 字典来存储配置参数，包括：

- `output_folder`：输出文件夹路径。
- `input_folder`：输入文件夹路径。
- `voice`：语音类型，默认为 `zh-CN-XiaoxiaoNeural`。
- `rate`：语速，默认为 `+0%`。
- `volume`：音量，默认为 `+0%`。
- `batch_size`：批处理大小，默认为 `20`。

## 使用方法

1. **设置输入文件夹**：确保输入文件夹中包含需要转换的文本文件。如果输入文件夹不存在，脚本会提示用户输入新的文件夹路径。
2. **运行脚本**：运行脚本后，程序会自动处理输入文件夹中的所有文本文件，并将生成的语音文件保存到输出文件夹中。
3. **查看进度**：脚本会显示处理进度，并在处理完成后显示总运行时间。

## 注意事项

- 确保输入文件夹中包含 `.txt` 格式的文本文件，并且文件按照01.txt,02.txt...15.txt或者001.txt,002.txt...850.txt进行命名，之后的更新可能会修改为按自然排序(2\<10)
- 如果输入文件夹中没有可处理的文件，脚本会提示用户并退出。
- 脚本会自动创建输出文件夹，如果输出文件夹不存在。

## 依赖库

- `edge_tts`：用于生成语音。
- `asyncio`：用于异步处理。
- `os`：用于文件和目录操作。
- `datetime`：用于记录时间。
- `sys`：用于系统操作。
- `tqdm`：用于显示进度条。

请确保你安装了它们