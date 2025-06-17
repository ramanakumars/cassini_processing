import glob
import os
from pysis.isis import ciss2isis
import re
import shutil
import tqdm

labels = sorted(glob.glob('./*/*.LBL'))

jupiter_lbls = sorted(glob.glob('jupiter_imgs/*.LBL'))

target_pattern = r'TARGET_NAME = "(\S+)"'
filter_pattern = r"FILTER_NAME = \(\"(?:(?:CL\d)|(\w+))\",\"(?:(?:CL\d)|(\w+))\"\)"

for label in tqdm.tqdm(labels):
    filename = os.path.basename(label)

    with open(label, 'r') as infile:
        label_data = infile.read()

    matches = re.findall(target_pattern, label_data)
    filter_matches = list(re.findall(filter_pattern, label_data)[0])
    filter_matches = list(filter(lambda e: e != '', filter_matches))

    if len(matches) > 0:
        if matches[0].lower() == 'jupiter':

            if len(filter_matches) > 1 or len(filter_matches) == 0:
                print(label)
                print(filter_matches)
                continue

            filter_name = filter_matches[0]

            if not os.path.exists(f'jupiter_imgs/{filter_name}'):
                os.makedirs(f'jupiter_imgs/{filter_name}')
            shutil.copyfile(label, f'jupiter_imgs/{filter_name}/{filename}')
            shutil.copyfile(label.replace('.LBL', '.IMG'), f'jupiter_imgs/{filter_name}/{filename.replace(".LBL", ".IMG")}')

            jupiter_lbls.append(f'jupiter_imgs/{filter_name}/{filename}')


for label in tqdm.tqdm(jupiter_lbls):
    outfile = label.replace('jupiter_imgs', 'cubs').replace('.LBL', '')
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))

    if os.path.exists(outfile + '.cub'):
        continue

    ciss2isis(from_=label, to=outfile)
