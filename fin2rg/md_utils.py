# encoding:utf-8
import re
from dataclasses import dataclass
from typing import Optional, List


class MdSection(object):
    def __init__(self, md_tile):
        self.level = -1
        self.simple_tile = md_tile
        self.title = md_tile
        self.lines = []
        self._parse_md_tile()
    def append_line(self, line):
        self.lines.append(line)
    def _parse_md_tile(self):
        m = re.match(r'^([#]+) ([\s\S]+)', self.title)
        if m:
            level_text = m.group(1).strip()
            simple_tile = m.group(2).strip().strip('、').strip('.')
            self.level = len(level_text)
            self.simple_tile = simple_tile
            # 针对doc2x处理
            if len(level_text) == 2:
                if re.match(r'^(第[一二三四五六七八九十]+节)',simple_tile):
                    self.level = 0
                    self.simple_tile = re.sub(r'^(第[一二三四五六七八九十]+节)', '',simple_tile)
                elif re.match(r'^([一二三四五六七八九十]+)',simple_tile):
                    self.level = 1
                    self.simple_tile = re.sub(r'^([一二三四五六七八九十]+)','', simple_tile)
                elif re.match(r'^([\d]+)',simple_tile):
                    self.level = 2
                    self.simple_tile = re.sub(r'^([\d]+)', '', simple_tile)
                elif re.match(r'^([(（] ?[\d]+ ?[)）])',simple_tile):
                    self.level = 3
                    self.simple_tile = re.sub(r'^([(（] ?[\d]+ ?[)）])', '', simple_tile)

            self.simple_tile = self.simple_tile.strip().strip().strip('、').strip('.')
    def get_content(self):
        return self.title + ''.join(self.lines)


def parse_md_file_to_section_list(md_file) -> List[MdSection]:
    ret = []
    with open(md_file, 'r') as f:
        lines = f.readlines()
        lines = ['# 全文'] + lines
        pre_section = None
        for line in lines:
            m = re.match(r'^[#]+ [\s\S]+', line)
            if m:  # 是标题
                if pre_section:
                    ret.append(pre_section)
                pre_section = MdSection(md_tile=line)
            else:
                pre_section.append_line(line)
        if pre_section:
            ret.append(pre_section)
    return ret

