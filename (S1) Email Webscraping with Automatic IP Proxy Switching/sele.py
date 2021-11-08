from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

url = 'http://cnpj.info/'
busca = "03 IRMAOS PRESTADORA DE SERVICOS"
"""
<div class=hdr itemscope itemtype="http://schema.org/WebSite">
<meta itemprop="url" content="http://cnpj.info/">
<form method=post action="/busca" itemprop="potentialAction" itemscope itemtype="http://schema.org/SearchAction">
<meta itemprop="target" content="http://cnpj.info/{q}">
<h3>Pesquisa: <input type=text name=q placeholder="Nome ou CNPJ ou telefone" size=30 itemprop="query-input" required> <input type=submit value="Buscar" title="Search/Lookup"></h3></form>
</div>
"""
browser = Firefox()
browser.get(url)

divclass = browser.find_element_by_class_name('hdr')
element = divclass.find_element_by_tag_name('h3')
insert = element.find_element_by_name('q')

#print(insert)

insert.send_keys(busca)
insert.send_keys(Keys.RETURN)

"""
<ul><li>CNPJ: <a href=/27316450000144>27.316.450/0001-44</a> | 27316450000144 [&nbsp;MATRIZ&nbsp;] - ATIVA&nbsp;desde&nbsp;2017-03-16<br>Nome: <a href=/Deniel-Willian-P-de-Castro-03-Irmaos-Prestadora-de-Servicos>Deniel Willian P de Castro</a><br>Fantasia nome: <a href=/Deniel-Willian-P-de-Castro-03-Irmaos-Prestadora-de-Servicos>03 Irmaos Prestadora de Servicos</a><br>Localização: Zona de Expansao Urbana, Terenos&nbsp;-&nbsp;MS
<li>CNPJ: <a href=/11040568000152>11.040.568/0001-52</a> | 11040568000152 [&nbsp;MATRIZ&nbsp;] - INAPTA&nbsp;desde&nbsp;2021-02-23<br>Nome: <a href=/J-Lomas-de-Souza-2-Irmaos-Prestadora-de-Servicos>J Lomas de Souza</a><br>Fantasia nome: <a href=/J-Lomas-de-Souza-2-Irmaos-Prestadora-de-Servicos>2 Irmaos Prestadora de Servicos</a><br>Localização: Mauazinho, Manaus&nbsp;-&nbsp;AM
<li>CNPJ: <a href=/27516078000110>27.516.078/0001-10</a> | 27516078000110 [&nbsp;MATRIZ&nbsp;] - INAPTA&nbsp;desde&nbsp;2021-02-23<br>Nome: <a href=/Claudio-Rodrigues-dos-Santos-Prestadora-de-Servicos-03-Irmaos>Claudio Rodrigues dos Santos</a><br>Fantasia nome: <a href=/Claudio-Rodrigues-dos-Santos-Prestadora-de-Servicos-03-Irmaos>Prestadora de Servicos 03 Irmaos</a><br>Localização: Centro, Porto Grande&nbsp;-&nbsp;AP
</ul>
"""

list = browser.current_url().find_element_by_tag_name('li')

print(list)