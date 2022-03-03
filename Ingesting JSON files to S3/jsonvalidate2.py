import os, os.path
import json

path = '/home/andreolv/Downloads/Empresa/Files/'

broken_fields = 0
valid_fields = 0

lista_arquivos = os.listdir(path)
lista_arquivos.sort()

json_fields = ['id', 'name', 'idade', 'credito_solicitado', 'data_solicitacao']

for arquivo in lista_arquivos:
    f = open(path + arquivo)

    data = json.load(f)

    for cliente in data['clientes']:
        for campo in json_fields:
            if (campo in cliente):
                valid_fields += 1
            else:
                print('File ' + arquivo + ' ,customer ' + cliente['id'] + ' does not have the field ' + campo)
                broken_fields += 1

print('\nTotal of files:', len(lista_arquivos))
print('Total of valid fields:', valid_fields)
print('Total of broken fields:', broken_fields)

f.close()

"""
Sugestions for improvements:
- Validate each json value by datatype
- Validade if there is a json field that is not expected
"""
