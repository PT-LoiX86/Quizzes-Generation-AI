

a=[]


s="""Beryli
Bo
Argon
Scandi
Titani
Vanadi
Chromi
Coban
Gali
Germani
Arsen
Seleni
Rubidi
Stronti
Ytri
Zirconi
Niobi
Molypden
Tecneti
Rutheni
Rhodi
Paladi
Cadmi
Indi
Stannum
Antimon
Teluri
Iod
Xenon
Caesi
Lanthan
Ceri
Praseodymi
Neodymi
Promethi
Samari
Europi
Gadolini
Terbi
Dysprosi
Holmi
Erbi
Thuli
Yterbi
Luteti
Hafni
Tantali
Wolfram
Rheni
Osmi
Iridi
Hydragyrum
Tali
Plumbum
Bismuth
Poloni
Astatin
Radon
Franci
Radi
Actini
Thori
Protactini
Urani
Neptuni
Plutoni
Americi
Curi
Berkeli
Californi
Einsteini
Fermi
Mendelevi
Nobeli
Lawrenci"""
s=s.replace("\n"," ")
s=s.replace('"',"")
a=s.split()
a=[name+".txt" for name in s.split() ]
for filename in a:
    open(filename,'w+')

















