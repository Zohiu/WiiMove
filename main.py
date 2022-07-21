# You need to have WIT installed. (To read id and name data from .wbfs files)
# https://wit.wiimm.de/wit/


import os
import sys
import subprocess


if __name__ == '__main__':
    sys.stdout.write(100 * f"\n ")
    drive_wbfs = input("Path to the drive\n» ")
    drive_wbfs = os.path.join(drive_wbfs, "wbfs")
    
    if not os.path.exists(drive_wbfs):
        os.mkdir(drive_wbfs)
    
    folders = []
    for i in os.scandir(os.getcwd()):
        if i.name != "main.py":
            folders.append(i.path)

    totalsize = 0
    for folder in folders:
        for file in os.scandir(folder):
            filetype = file.name.split(".")[-1]
            if filetype == "wbfs" or filetype == "wbf1":
                totalsize += os.path.getsize(file.path)/(1024*1024*1024)

    totalsize = round(totalsize, 2)
    print(f"\nCopying {len(folders)} games into {drive_wbfs}. {totalsize} GB total\n")
    
    for folder in folders:
        for file in os.scandir(folder):
            filetype = file.name.split(".")[-1]
            if filetype == "wbfs" or filetype == "wbf1":
                dump = subprocess.run(['wit', 'DUMP', f'{file.path.replace("wbf1", "wbfs")}'], stdout = subprocess.PIPE).stdout.decode('utf-8')
                disc_id = dump.split(', wbfs=')[1].split('\n  Disc name:')[0]
                disc_name = dump.split('Disc name:         ')[1].split('\n  ID Region:')[0].replace(":", "")
                
                path = os.path.join(drive_wbfs, f"{disc_name} [{disc_id}]")
                
                sys.stdout.write('\r'*2 + f'Copying .{filetype} of "{folder.split(os.sep)[-1]}" ({file.name.split(".")[0]})...                   \n')
                if not os.path.exists(path):
                    os.mkdir(path)
                
                source = file.path
                
                target = os.path.join(path, file.name)
                
                source_size = os.path.getsize(file.path)
                totalsize -= source_size/(1024*1024*1024)
                
                with open(source, 'rb') as fsrc:
                    with open(target, 'wb') as fdst:
                        while True:
                            try:
                                buf = fsrc.read(16 * 1024)
                                if not buf:
                                    break
                                fdst.write(buf)
                                
                                target_size = os.path.getsize(target)
                                fraction = target_size / source_size
                                
                                arrow = int(fraction * 25 - 1) * '-' + '>'
                                padding = int(25 - len(arrow)) * ' '
                                
                                sys.stdout.write('\r' + f'Progress: [{arrow}{padding}] {int(fraction*100)}% ({round(target_size/(1024*1024*1024), 2)} / {round(source_size/(1024*1024*1024), 2)} GB)')
                                
                                if source_size == target_size:
                                    sys.stdout.write('\r'*2 + 100*" ")
                                    break
                                    
                            except KeyboardInterrupt:
                                sys.stdout.write('\n')
                                sys.exit()
                                
                sys.stdout.write('\r' + 100*" ")
                
        sys.stdout.write('\r' + f'Progress: [{arrow}{padding}] {int(100)}%')
        sys.stdout.write(f'\r{100*""}' * 2 + f'\n{100*" "}\nCopied "{folder.split(os.sep)[-1]}". ({folders.index(folder) + 1} of {len(folders)} games. {round(totalsize, 2)} GB remaining.){100*" "}\n{100*" "}\n{100*" "}')