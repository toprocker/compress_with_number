import argparse
import math
import os
import zipfile
from multiprocess import Pool, cpu_count


class ZFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def addfile(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.addfile(*path)
            else:
                self.addfile(path)

    def close(self):
        self.zfile.close()

    def extract_to(self, path):
        self.zfile.extractall(path)
        # for p in self.zfile.namelist():
        #     self.extract(p, path)

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            self.zfile(f, 'wb').write(self.zfile.read(filename))


def create(x):
    zfile, files = x
    z = ZFile(zfile, 'w')
    z.addfiles(files)
    z.close()
    print("finish",zfile)


def extract(x):
    zfile, path = x
    z = ZFile(zfile)
    z.extract_to(path)
    z.close()
    print("finish",zfile)


def split_file_list():
    total_list = os.listdir(opt.folder) if not opt.ref else sorted(list(set(os.listdir(opt.folder))-set(os.listdir(opt.ref))))
    total_length = len(total_list)
    print(f"指定文件夹下需要压缩的文件总共有{total_length}个")
    part_lists = [[os.path.join(opt.folder,total_list[i]) for i in range(p*opt.num,p*opt.num+opt.num) if i<total_length]
                  for p in range(math.ceil(total_length/opt.num))]
    print(f"每{opt.num}个文件压缩为一部分，总共有{len(part_lists)}个部分，最后一个部分包含{len(part_lists[-1])}个文件")
    return part_lists


def create_per_num():
    part_lists = split_file_list()
    with Pool(cpu_count()) as p:
        p.map(create, list(zip([opt.name + str(i) + ".zip" for i in range(len(part_lists))], part_lists)))


def extract_per_num():
    zip_files = [opt.name + str(i) + ".zip" for i in range(opt.num)]
    with Pool(cpu_count()) as p:
        p.map(extract, list(zip(zip_files, [opt.folder]*len(zip_files))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, default='/path/to/folder', help="压缩时指压缩路径，解压时指解压路径")
    parser.add_argument("--ref", type=str, default=None, help="只压缩folder文件夹下ref文件夹中没有的文件")
    parser.add_argument("--num", '-n', type=int, default=10000, help="压缩时num为每部分文件数，解压时num为部分总数")
    parser.add_argument("--name", type=str, default='outfile', help="不需要输入.zip后缀，解压时也不需要输入数字")
    opt = parser.parse_args()
    create_per_num()
    # extract_per_num()
    # 解压也可以通过   for f in ls *.zip;do unzip $f & done; wait
