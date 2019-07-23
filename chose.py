import sys, os
import json, codecs
import itertools
import logging

def get_data(name):
    with codecs.open(os.path.join('.','data',name+'.json'),'r','utf-8') as f:
        data = json.load(f)
    return data

class Lineup_Selector(object):
    def __init__(self):
        self.__heros = get_data('hero')
        self.__bufflevel = get_data('bufflevel')
    
    #获取英雄及等级对应
    def hero_level(self, heros):
        hero_level = {}
        for hero in heros:
            hero_level[hero[:-1]] = int(hero[-1])
        return [hero[:-1] for hero in heros], hero_level

    #统计此阵容下各buff出现次数
    def buff_statics(self, heros, new_buff):
        buffs = {}
        for buff in new_buff:
            buffs[buff]  = 1
        for hero in heros:
            if hero not in self.__heros.keys():
                logging.error('Wrong Hero Name : %s ' % hero)
                return None
            else:
                for feature in self.__heros[hero]:
                    if feature  in buffs.keys():
                        buffs[feature] += 1
                    else:
                        buffs[feature] = 1
        return buffs
    
    #根据各buff统计出现次数，得到场上生效buff数
    def buff_in_force(self, buffs):
        exist_buffs = 0
        buff_detail =[]
        for buff in buffs:
            exist_time  = buffs[buff]
            level_dict = self.__bufflevel[buff]
            buff_num = 0
            min_dist = 9999
            get_buff_flag = False
            for level in level_dict.keys():
                level_dist = exist_time - int(level)
                if level_dist  >= 0 and level_dist <= min_dist:
                    get_buff_flag = True
                    min_dist = level_dist
                    buff_num = level_dict[level]
            if get_buff_flag:
                exist_buffs += buff_num
                buff_detail.append(buff+str(buff_num))
        return exist_buffs, buff_detail

    #计算英雄等级之和
    def team_level(self, heros, heros_level):
        level_sum = 0
        for hero in heros:
            level_sum += heros_level[hero]
        return level_sum

    #获取目前所有可能的上场阵容，及对应的buff数和等级之和
    def get_teams(self, heros, lineup_num, must_have = [], new_buff = []):
        heros, heros_level = self.hero_level(heros)
        teams = itertools.combinations(heros, lineup_num)
        team_id = 0
        team_dict = {}
        buff_num_dict = {}
        buff_detail_dict = {}
        team_level_dict = {}
        for team in teams:
            have_flag = True
            for have in must_have:
                if have not in team:
                    have_flag = False
                    break
            if not have_flag:
                continue
            team_buff_num, team_buff_detail = self.buff_in_force(self.buff_statics(team, new_buff))
            team_level_sum = self.team_level(team, heros_level)
            team_dict[team_id] = team
            buff_num_dict[team_id] = team_buff_num
            buff_detail_dict[team_id] = team_buff_detail
            team_level_dict[team_id] = team_level_sum
            team_id += 1
        return team_dict, buff_num_dict, buff_detail_dict, team_level_dict
    
    #获取最大值
    def top_value(self, value_dict, top = 1):
        value_rank = sorted(list(set(value_dict.values())),  reverse = True)
        if top > len(value_rank):
            return value_rank
        else:
            return value_rank[:top]

    #选取产生buff最多的上场阵容并输出
    def select(self, heros, lineup_num, mode = 'BUFF_FIRST', must_have  = [], new_buff = []):
        if isinstance(heros, str):
            heros = heros.split()
        team_dict, buff_num, buff_detail, level_sum = self.get_teams(heros, lineup_num, must_have, new_buff)
        if mode == 'BUFF_FIRST':
            buff_top_value = self.top_value(buff_num)[0]
            level_rank = {}
            for team_id in buff_num.keys():
                if buff_num[team_id] == buff_top_value:
                    level_rank[team_id] = level_sum[team_id]
            
            level_top_value = self.top_value(level_rank)[0]
            print(' ')
            print(' ')
            for team_id in level_rank.keys():
                if level_rank[team_id] == level_top_value:
                    print('==========================================')
                    print('排名：1' )
                    print('阵容：', team_dict[team_id])
                    print('平均等级：',  round(level_top_value/len(team_dict[team_id]), 2))
                    print('Buff数量：', buff_num[team_id])
                    print('Buff详细：', buff_detail[team_id])
        elif mode == 'LEVEL_FIRST':
            level_top_value = self.top_value(level_sum, top = 3)[0]
            print(level_top_value)
            buff_rank = {}
            for team_id in level_sum.keys():
                if level_sum[team_id] >= level_top_value:
                    buff_rank[team_id] = buff_num[team_id]
            
            buff_top_value = self.top_value(buff_rank, top = 3)
            print(' ')
            print(' ')
            show_num = 0
            end_flag = False
            for i in range(0, len(buff_top_value)):
                if end_flag:
                    break
                for team_id in buff_rank.keys():
                    if buff_rank[team_id] == buff_top_value[i]:
                        show_num += 1
                        if show_num > 3:
                            print('--------------------------------more---------------------------')
                            end_flag = True
                            break
                        print('==========================================')
                        print('排名：', str(i+1) )
                        print('阵容：', team_dict[team_id])
                        print('平均等级：',  round(level_sum[team_id]/len(team_dict[team_id]), 2))
                        print('Buff数量：', buff_num[team_id])
                        print('Buff详细：', buff_detail[team_id])

def get_stat(line):
    if '上场人数' in line:
        return 1
    elif '拥有英雄' in line:
        return 2
    elif '必须上场' in line:
        return 3
    elif '新增BUFF' in line:
        return 4
    elif '模式' in line:
        return 5
    else:
        return 0

if __name__ == '__main__':
    ls = Lineup_Selector()
    #heros = ['盖伦','VN', '剑姬', '卢锡安', '日女', '天使']
    #heros = '盖伦 VN 剑姬 卢锡安 日女 天使'
    #print(ls.buff_statics(heros))
    #print(ls.buff_in_force(ls.buff_statics(heros)))
    #print(ls.get_teams(heros, 3))
    #ls.select(heros, 3, top = 1)

    #heros = '狼人3 VN2 剑姬2 慎1 机器人2 寒冰2 天使1 千珏1 大虫子2 德莱文1 火男1 日女2'
    with codecs.open('./Record/runtime','r','utf-8') as f:
        lines = f.readlines()
    num = 0
    heros = []
    must_have = []
    new_buff = []
    mode = ''
    argv_flag = 0

    for line in lines:
        if line.strip() == '':
            continue
        stat = get_stat(line)
        if not stat:
            if argv_flag == 1:
                num = int(line.strip())
            elif argv_flag == 2:
                heros.append(line.strip())
            elif argv_flag == 3:
                must_have.append(line.strip())
            elif argv_flag == 4:
                new_buff.append(line.strip())
            elif argv_flag == 5:
                if line.strip() == '0':
                    mode = 'BUFF_FIRST'
                elif line.strip() == '1':
                    mode = 'LEVEL_FIRST'
        else:
            argv_flag = stat
    #print(num)
    #print(heros)
    #print(must_have)
    #print(new_buff)
    ls.select(heros, num, mode, must_have, new_buff)



