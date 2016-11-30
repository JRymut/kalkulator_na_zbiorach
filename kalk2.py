# coding=utf-8

import string

class NieMaTakiejZmiennej(Exception): pass

class NiepoprawnaInstrukcja(Exception): pass

class Instrukcja:
    def __init__(self, Zmienna, wyrazenie):
        self.zmienna = Zmienna
        self.wyrazenie = wyrazenie

class Przypisanie(Instrukcja):
    def exe(self, kalk):
        kalk.zmienne[self.zmienna.nazwa] = kalk.policz_wyrazenie(self.wyrazenie)
        return ""


class Przypisanie_Odroczone(Instrukcja):
    def exe(self, kalk):
        kalk.zmienne[self.zmienna.nazwa] = self.wyrazenie
        return ""


class Wyswietl(Instrukcja):
    def exe(self, kalk):
        if isinstance(self.wyrazenie, list) and len(self.wyrazenie) == 1 and isinstance(self.wyrazenie[0], Zmienna) and not self.wyrazenie[0].istnieje(kalk):
            raise NieMaTakiejZmiennej
        wynik = kalk.policz_wyrazenie(self.wyrazenie)
        return str(wynik)

class Wyrazenie: pass

class Zbior(Wyrazenie):
    def __init__(self, elementy, nazwa=None):
        self.elementy = elementy
        self.nazwa = nazwa

    def lista_na_napis(self, lista):
        if len(lista) == 0:
            return ""
        zwracany = "{"
        for element in lista:
            if isinstance(element, (list, tuple)):
                zwracany += self.lista_na_napis(element) + " "
            else:
                zwracany += str(element) + " "
        if zwracany[-1] == " ":
            zwracany = zwracany[:-1]
        zwracany += "}"
        return zwracany

    def __str__(self):
        return self.lista_na_napis(self.elementy)

    def __repr__(self):
        return self.__str__()

    def licz(self, kalk):
        zliczone_elementy = []
        for element in self.elementy:
            if not isinstance(element, int):
                try:
                    element = element.licz(kalk)
                except NieMaTakiejZmiennej as exception:
                    pass
            zliczone_elementy.append(element)
        return Zbior(zliczone_elementy)

class PrzejsciowyZbior(Zbior): pass

class Zmienna(Wyrazenie):
    def __init__(self, nazwa):
        self.nazwa = nazwa

    def licz(self, kalk):
        if self.istnieje(kalk):
            return kalk.policz_wyrazenie(kalk.zmienne[self.nazwa])
        else:
            return Zbior(None, self.nazwa)

    def istnieje(self, kalk):
        return kalk.zmienne.__contains__(self.nazwa)

    def __str__(self):
        return self.nazwa

    def __repr__(self):
        return str(self.nazwa)


class Operator:
    def __init__(self, op):
        self.op = op


class Operacja(Wyrazenie):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2


class Dodawanie(Operacja):
    def licz(self, kalk):
        if self.operand1.elementy == None:
            return PrzejsciowyZbior([self.operand1.nazwa, "u", self.operand2.elementy])
        elif self.operand2.elementy == None:
            return PrzejsciowyZbior([self.operand1.elementy, "u", self.operand2.nazwa])
        else:
            suma = []
            suma.extend(self.operand1.licz(kalk).elementy)
            suma.extend(self.operand2.licz(kalk).elementy)
            return Zbior(list(set(suma)))

    def __str__(self):
        return self.operand1 + " u " + self.operand2

    def __repr__(self):
        return str(self)


class Wspolne(Operacja):
    def licz(self, kalk):
        if self.operand1.elementy == None:
            return PrzejsciowyZbior([self.operand1.nazwa, "n", self.operand2.elementy])
        elif self.operand2.elementy == None:
            return PrzejsciowyZbior([self.operand1.elementy, "n", self.operand2.nazwa])
        else:
            przeciecie = set(self.operand1.licz(kalk).elementy) & set(self.operand2.licz(kalk).elementy)
            return Zbior(list(przeciecie))


class Roznica(Operacja):
    def licz(self, kalk):
        if self.operand1.elementy == None:
            return PrzejsciowyZbior([self.operand1.nazwa, "\\", self.operand2.elementy])
        elif self.operand2.elementy == None:
            return PrzejsciowyZbior([self.operand1.elementy, "\\", self.operand2.nazwa])
        else:
            subtraction = set(self.operand1.licz(kalk).elementy) - set(self.operand2.licz(kalk).elementy)
            return Zbior(list(subtraction))


class Quasi(Operacja):
    def licz(self, kalk):
        if self.operand1.elementy == None:
            return PrzejsciowyZbior([self.operand1.nazwa, "x", self.operand2.elementy])
        elif self.operand2.elementy == None:
            return PrzejsciowyZbior([self.operand1.elementy, "x", self.operand2.nazwa])
        else:
            operand1_val = self.operand1.licz(kalk).elementy
            operand2_val = self.operand2.licz(kalk).elementy
            wynik = []
            for el1 in operand1_val:
                for el2 in operand2_val:
                    wynik.append(Zbior([el1, el2]))
            return Zbior(wynik)

nawias = ["(", ")"]
op = ["n", "u", "\\", "x"]
num = string.digits
litery = string.ascii_uppercase


class Parser:
    def rozbior_wyrazenia(self, napis):
        zmieniony = napis.replace(" ", "")
        if zmieniony[0] == "$":
            return Wyswietl(None, self.sprawdzenie_wyrazenia(napis[napis.find("$") + 1::]))
        elif zmieniony.find("=:") != -1:
            zmieniony = zmieniony.split("=:")
            return Przypisanie_Odroczone(Zmienna(zmieniony[0]), self.sprawdzenie_wyrazenia(napis[napis.find("=:") + 2::]))
        elif zmieniony.find("=") != -1:
            zmieniony = zmieniony.split("=")
            return Przypisanie(Zmienna(zmieniony[0]), self.sprawdzenie_wyrazenia(napis[napis.find("=") + 1::]))
        raise Exception("Zla Instrukcja")

    def sprawdzenie_wyrazenia(self, napis):
        if len(napis) == 0:
            raise Exception("Brak instrukcji")
        else:
            return self.stworz_liste_tokenow(napis)

    def stworz_liste_tokenow(self, napis):
        tokeny = []
        while len(napis) != 0:
            token, napis = self.stworz_tokeny(napis)
            tokeny.append(token)
        return tokeny

    def stworz_tokeny(self, napis):
        wynik = []
        while len(napis) != 0 and napis[0] == " ":
            napis = napis[1::]
        if napis[0] in litery:
            return self.stworz_zmienna(napis)
        elif napis[0] in num:
            return self.stworz_stala(napis)
        elif napis[0] in op:
            return self.stworz_operator(napis)
        elif napis[0] == "(":
            napis = napis[1::]
            return "(", napis
        elif napis[0] == ")":
            napis = napis[1::]
            return ")", napis
        elif napis[0] == "{":
            return self.stworz_zbior(napis)

    def stworz_zbior(self, napis):
        zbior = ""
        licznik_otw = 0
        licznik_zam = 0
        for el in napis:
            if el == "{":
                licznik_otw += 1
                zbior += el
                napis = napis[1::]
            elif el == "}":
                zbior += el
                licznik_zam += 1
                napis = napis[1::]
                if licznik_otw == licznik_zam:
                    zbior = zbior[1:-1]
                    return Zbior(self.stworz_liste_tokenow(zbior)), napis
            else:
                zbior += el
                napis = napis[1::]

    def stworz_operator(self, napis):
        op_znak = napis[0]
        napis = napis[1::]
        return Operator(op_znak), napis

    def stworz_stala(self, napis):
        num_znak = ""
        while len(napis) != 0 and napis[0] in num:
            num_znak += napis[0]
            napis = napis[1::]
        return int(num_znak), napis

    def stworz_zmienna(self, napis):
        zmienna = ""
        for el in napis:
            if el in litery:
                zmienna += el
                napis = napis[1::]
            else:
                break
        return Zmienna(zmienna), napis


class Kalkulator:
    def __init__(self, parser):
        self.zmienne = {}
        self.parser = parser

    def run(self, str):
        if len(str.replace(" ", "")) == 0:
            return ""
        return self.parser.rozbior_wyrazenia(str).exe(self)

    def policz_wyrazenie(self, wyrazenie):
        if not isinstance(wyrazenie, list):
            return wyrazenie.licz(self)
        wynik = []
        pomocnicza = []
        for token in wyrazenie:
            if isinstance(token, Zbior) or isinstance(token, Zmienna):
                wynik.append(self.policz_wyrazenie(token))
            elif isinstance(token, Operator):
                if len(pomocnicza) == 0 or pomocnicza[-1] == "(":
                    pomocnicza.append(token)
                else:
                    while pomocnicza[-1] != "(":
                        wynik.append(pomocnicza.pop())
                    pomocnicza.append(token)
            elif token == "(":
                pomocnicza.append(token)
            elif token == ")":
                if not pomocnicza:
                    raise Exception("Zle wyrazenie")
                else:
                    top = pomocnicza.pop()
                    while top != "(":
                        wynik.append(top)
                        top = pomocnicza.pop()
            else:
                raise Exception("Zle wyrazenie")

        while len(pomocnicza) > 0:
            wynik.append(pomocnicza.pop())
        return self.ONP_licz(wynik)

    def ONP_licz(self, ONP):
        wyrazenie = []
        for token in ONP:
            if isinstance(token, Zbior) or isinstance(token, Zmienna):
                wyrazenie.append(token)
            else:
                operand2 = wyrazenie.pop()
                operand1 = wyrazenie.pop()
                if token.op == "u":
                    wynik = Dodawanie(operand1, operand2).licz(self)
                if token.op == "\\":
                    wynik = Roznica(operand1, operand2).licz(self)
                if token.op == "x":
                    wynik = Quasi(operand1, operand2).licz(self)
                if token.op == "n":
                    wynik = Wspolne(operand1, operand2).licz(self)
                wyrazenie.append(wynik)
        return wyrazenie[0]

    def licz(self, tokens):
        return self.policz_wyrazenie(tokens)


if __name__ == "__main__":
    c = Kalkulator(Parser())
    while True:
        try:
            wpisywane = raw_input('')
            print c.run(wpisywane)
        except NieMaTakiejZmiennej:
            print "Podana zmienna nie istnieje"
