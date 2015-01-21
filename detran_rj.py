#!/usr/bin/env python3
# coding: utf-8

import json
import os
import sys
import time

import requests


URL = 'http://simulado.detran.rj.gov.br/simulados/iniciarProva/habilitacao'

def keys_to_lower(old_dict):
    return {key.lower(): value for key, value in old_dict.items()}

def pega_questoes():
    response = requests.get(URL)

    questoes_js = response.text.split('<script>')[1].split('};\r\n')[0] + u'}'
    questoes_js = questoes_js.replace(u'var questoes = ', u'')
    questoes = json.loads(questoes_js)['Questao']

    novas_questoes = []
    for questao in questoes:
        if not questao:
            continue
        questao = keys_to_lower(questao)
        nova_questao = {'enunciado': questao['desc_questao'],
                        'opcoes': [questao['resposta1'], questao['resposta2'],
                                   questao['resposta3'], questao['resposta4']],
                        'resposta_correta': questao['respcorreta'],
                        'imagem': questao['codigoimagem'],
                        'repeticoes': 1}
        novas_questoes.append(nova_questao)
    return novas_questoes

def log(message, to=sys.stdout):
    message = u'{} {}\n'.format(time.strftime(u'[%Y-%m-%d %H:%M:%S]'), message)
    to.write(message)
    to.flush()

def grava_json(filename, data):
    log(u'Gravando arquivo JSON "{}"...'.format(filename))
    with open(filename, 'w') as fobj:
        json.dump(data, fobj)
    log(u'Gravação finalizada.')

def main():
    json_filename = u'detran-rj.json'
    if not os.path.exists(json_filename):
        db = {}
        log(u'Arquivo JSON "{}" não encontrado.'.format(json_filename))
    else:
        with open(json_filename) as fobj:
            db = json.load(fobj)
        log(u'Utilizando arquivo JSON "{}" ({} questões).'
            .format(json_filename, len(db)))

    while True:
        try:
            questoes_anteriores = len(db)
            for questao in pega_questoes():
                enunciado = questao['enunciado']
                if enunciado in db:
                    db[enunciado]['repeticoes'] += 1
                else:
                    db[enunciado] = questao

            total_de_questoes = len(db)
            novas_questoes = total_de_questoes - questoes_anteriores
            log(u'Novas questões: {:02d}. Total: {:05d}'
                .format(novas_questoes, total_de_questoes))

            grava_json(json_filename, db)
        except KeyboardInterrupt:
            log(u'Interrupção recebida. Parando requisições.')
            grava_json(json_filename, db)
            break


if __name__ == '__main__':
    main()