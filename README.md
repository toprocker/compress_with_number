按文件数目多进程压缩，多进程解压 

多进程压缩 /path/to/src/ 文件夹(该文件下没有文件夹，都是文件)，每1000个文件一个包，包名前缀为outfile
```shell
python3 zip_per_num.py --folder=/path/to/src/ --num=1000 --name=outfile
```

多进程解压 所有前缀为outfile包 到 /path/to/dst/下 ，假设前缀为outfile包的个数为268
```shell
python3 zip_per_num.py --unzip --folder=/path/to/dst/ --num=268 --name=outfile
```
也可以在终端里利用unzip多进程解压
```shell
for f in ls outfile*.zip;do unzip $f -d /path/to/dst/ & done;
```