# Skills

### 使用方法

要打包某个特定的技能，请运行 `make` 命令并跟上该技能的目录名称。例如，要打包 `wechat-article-reader` 技能：

```bash
make wechat-article-reader
```

这个命令将会：
1. 进入 `wechat-article-reader` 目录。
2. 将该目录下的所有文件压缩成一个位于根目录的 `wechat-article-reader.zip` 文件（自动排除类似 `.DS_Store` 的无关文件）。
3. 生成的 `.zip` 文件随后即可直接上传或导入到 OpenClaw 中使用。

### 清理文件

要删除根目录下所有生成的 `.zip` 压缩包文件，请运行：

```bash
make clean
```
