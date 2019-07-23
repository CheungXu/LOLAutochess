import json, codecs

def heros2buffs(heros_path, buffs_path):
    with codecs.open(heros_path,'r','utf-8') as f:
        heros = json.load(f)
    buffs = {}
    for hero in heros.keys():
        for feature in heros[hero]:
            if feature not in buffs.keys():
                buffs[feature] = [hero]
            else:
                buffs[feature].append(hero)
    for feature in buffs.keys():
        print(feature,len(buffs[feature]),buffs[feature])
    with codecs.open(buffs_path,'w','utf-8') as f:
        json.dump(buffs,f)

    with codecs.open(heros_path,'w','utf-8') as f:
        json.dump(heros,f)

def json_trans(path):
    with open(path, 'r') as f:
        d = json.load(f)
    with open(path, 'w') as f:
        json.dump(d,f)

if __name__ == '__main__':
    #heros2buffs('hero.json','buffs.json')
    pass
