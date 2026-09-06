import logging
import random
import asyncio
import os
from aiohttp import web

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================================================
# BOT TOKEN VA SOZLAMALAR
# =========================================================

TOKEN = "8817043244:AAGJ8ooYXAmy4EPs4H6FO1zy1g0OVv_-fwk"
AUTHOR_NAME = "Reyimbayev Bahrom Maxsudovich"

# DIQQAT: O'z Telegram ID raqamingizni shu yerga yozing!
# (@userinfobot orqali ID raqamingizni bilib olishingiz mumkin)
ADMIN_ID = 5637205211  # Misol: ADMIN_ID = 123456789

# Barcha qatnashuvchilar tarixini saqlash
history_records = []

# =========================================================
# TEST SAVOLLARI (72 TA)
# =========================================================

questions = [
    {
        "q": "O‘q otish asoslariga nima kiradi?",
        "options": [
            "Belgilangan vaqt oralig‘ida qurolning moddiy qismlariga, xavfsizlik choralariga ziyon yetkazmay va o‘q otish natijalarini yomonlashtirmay eng ko‘p miqdorda otish asoslari.",
            "Aylanayotgan o‘qning trayektoriyasini, og‘irlik kuchi va yo‘nalishini o‘rgatuvchi qonuni.",
            "Ichki ballistika, tashqi ballistika va o‘qlarning yoyilish qonuni.",
            "O‘qning fazodagi xarakatini o‘rgatuvchi fan."
        ],
        "answer": 2
    },
    {
        "q": "To‘g‘ridan-to‘g‘ri otish deb nimaga aytiladi?",
        "options": [
            "Trayektoriyasi mo‘ljallanish chizig‘ida nishondan balandga ko‘tarilib otish.",
            "O‘qning (granataning) yonlama va uzoqlik (balandlik) bo‘yicha yoyilishiga asosan otish.",
            "Trayektoriyaga urinma va qurol gorizonti orasidagi masofaga aytiladi.",
            "Trayektoriyasi mo‘ljallanish chizig‘ida nishondan balandga ko‘tarilmaydigan otish."
        ],
        "answer": 3
    },
    {
        "q": "O‘q uzilish jarayoni necha davrdan iborat?",
        "options": [
            "O‘q otishda 4 ta ketma-ket davr mavjud: Oldingi, birinchi yoki asosiy davr, ikkinchi davr, uchinchi davr, yoki gazlar ta’siridan keyingi davr.",
            "O‘q otishda 6 ta ketma-ket davr mavjud: Oldingi, birinchi, asosiy davr, ikkinchi davr, uchinchi davr, gazlar ta’siridan keyingi davr.",
            "O‘q otishda 4 ta ketma-ket davr mavjud: Asosiy davr, birinchi davr, ikkinchi davr, gazlar ta’siridan keyingi davr.",
            "O‘q otishda 3 ta ketma-ket davr mavjud: Birinchi, asosiy davr, ikkinchi davr, uchinchi davr, gazlar ta’siridan keyingi davr."
        ],
        "answer": 0
    },
    {
        "q": "O‘qning boshlang‘ich tezligi deb nimaga aytiladi?",
        "options": [
            "Stvolning uzunligiga, o‘qning og‘irligiga, porox zaryadining haroratini va namligiga, porox zarralarining shakl va o‘lchamlariga hamda o‘qlanish zichligiga bog‘liq xarakati boshlang‘ich tezlik deb ataladi.",
            "O‘qning stvolning og‘iz kesimi yaqinidagi harakat tezligi boshlang‘ich tezlik deb ataladi.",
            "O‘qning stvoldan chiqishi va nishongacha tezlik bilan borib tegishi boshlang‘ich tezlik deb ataladi.",
            "Qurolning tepinishi yelkaga, qo‘lga va yerga kuch bilan urilish boshlang‘ich tezlik deb ataladi."
        ],
        "answer": 1
    },
    {
        "q": "O‘q uzish deb nimaga aytiladi?",
        "options": [
            "O‘q uzish deb porox zaryadining yonishi natijasida hosil bo‘lgan gazlar energiyasi ta’sirida stvol kanalidan o‘qning (granataning) otilib chiqishiga (irg‘itilishiga) aytiladi.",
            "O‘q uzish deb stvolning uzunligiga, o‘qning og‘irligiga, porox zaryadining harorati va namligiga, porox zarralarining shakl va o‘lchamlariga hamda o‘qlanish zichligiga bog‘liq tartibda stvoldan otilib chiqishiga aytiladi.",
            "Porox gazlarining yuqori harorati, stvol kanalining vaqti-vaqti bilan kengayishi va uning boshlang‘ich holatga qaytishi o‘q uzish deb aytiladi.",
            "O‘q uzish deb o‘qdorilarning yonishi natijasidagi gazlarining yuqori harorati nitijasida stvoldan otilib chiqishiga o‘q uzish deb aytiladi."
        ],
        "answer": 0
    },
    {
        "q": "Ichki ballistika nima?",
        "options": [
            "O‘qning (granataning) porox gazlari ta’siri tugagandan keyin harakatlarini o‘rganuvchi fan.",
            "Otish paytida hosil bo‘ladigan jarayonlarni, xususan o‘q (granata)ning stvol kanalida harakatlanishini o‘rganuvchi fan.",
            "O‘qlarning yoyilish qonuni o‘rganuvchi fan.",
            "Otishdan so‘ng hosil bo‘ladigan jarayonlarni, xususan o‘q (granata)ning patronnikda harakatlanishini o‘rganuvchi fan."
        ],
        "answer": 1
    },
    {
        "q": "Tepinish deb nimaga aytiladi?",
        "options": [
            "Trayektoriyaga urinma va qurol gorizonti orasidagi tepinishga aytiladi.",
            "Yelkaga, qo‘lga va yerga kuch bilan urilish tepinish deb aytiladi.",
            "O‘q otish paytida qurol (stvol)ning orqaga harakatlanishiga aytiladi.",
            "Qo‘ndoq orqali qo‘rol (stvol)ning yelkagi kuch bilan urilish tepinish deb aytiladi."
        ],
        "answer": 2
    },
    {
        "q": "Stvolning yeyilishini keltirib chiqaruvchi sabablar:",
        "options": [
            "O‘q otish jarayonida stvol yeyiladi. Stvolning yeyilish sabablarini uchta asosiy guruhlarga – avtomatik, mexanik va fizik xarakterdagi sabablarga bo‘lish mumkin.",
            "O‘q otish jarayonida stvol yeyiladi. Stvolning yeyilish sabablarini uchta asosiy guruhlarga – avtomatik, fizik va kimyoviy xarakterdagi sabablarga bo‘lish mumkin.",
            "O‘q otish jarayonida stvol yeyiladi. Stvolning yeyilish sabablarini uchta asosiy guruhlarga – jismoniy, fizik va kimyoviy xarakterdagi sabablarga bo‘lish mumkin.",
            "O‘q otish jarayonida stvol yeyiladi. Stvolning yeyilish sabablarini uchta asosiy guruhlarga – kimyoviy, mexanik va termik xarakterdagi sabablarga bo‘lish mumkin."
        ],
        "answer": 3
    },
    {
        "q": "Stvol mustahkamligi deb nimaga ataladi?",
        "options": [
            "O‘qotar qurollarning xromlangan stvollari kuchliligiga o‘q uzishlarga aytiladi.",
            "Belgilangan vaqt oralig‘ida qurolning moddiy qismlariga, xavfsizlik choralariga ziyon yetkazmay va o‘q otish natijalarini yomonlashtirmay eng ko‘p miqdorda otishiga aytiladi.",
            "Stvol kanalida stvol devorlarining ma’lum gazlar bosimini ushlab turuvchi qobiliyati aytiladi.",
            "Stvolning belgilangan miqdordagi o‘qning otilishiga chidab berishiga aytiladi."
        ],
        "answer": 2
    },
    {
        "q": "Tashqi ballistika nima?",
        "options": [
            "Har xil sharoitlarda faqat birgina quroldan otish paytida o‘q (granata)larning yoyilish hodisasini, o‘q (granata)larning tabiiy yoyilishini hamda trayektoriyasini o‘rgatuvchi fan.",
            "Har xil sharoitlarda quroldan otish paytida o‘qning trayektoriyasini o‘rgatuvchi fan.",
            "O‘qning (granataning) havoda uchish jarayonida og‘irlik markazi hosil qiladigan jarayon, hamda yerning yuzasiga va havoning zichligiga bog‘liqligini o‘rganuvchi fan.",
            "O‘qning (granataning) porox gazlari ta’siri tugagandan keyin harakatlarini o‘rganuvchi fan."
        ],
        "answer": 3
    },
    {
        "q": "Otish rejimi deb nimaga aytiladi?",
        "options": [
            "Ko‘rsatilgan vaqt oralig‘ida o‘qning (granataning) porox gazlari ta’siri tugagandan keyingi harakatlarini o‘rganuvchi jarayon otish rejimi deb aytiladi.",
            "Belgilangan vaqt oralig‘ida qurolning moddiy qismlariga, xavfsizlik choralariga ziyon yetkazmay va o‘q otish natijalarini yomonlashtirmay eng ko‘p miqdorda otishiga aytiladi.",
            "O‘qning otish tekisligidan aylanish tomonga qarab og‘ishi otish rejimi deb aytiladi.",
            "Ko‘rsatilgan vaqt oralig‘ida o‘qdorilarning moddiy qismlariga, o‘q otish natijalarini yomonlashtirish orqali eng kam miqdorda sarf qilinishi otish rejimi deb aytiladi."
        ],
        "answer": 1
    },
    {
        "q": "Derivatsiya deb nimaga ataladi?",
        "options": [
            "Havo qarshilik kuchining kattaligi o‘qning (granataning) uchish tezligiga, kalibriga va shakliga, hamda uning yuzasiga va havoning zichligiga bog‘liqligiga aytiladi.",
            "O‘qning otish tekisligidan aylanish tomonga qarab og‘ishi va shu bilan birgalikda o‘qning aylanma harakati, havoning qarshiligi va og‘irlik kuchi ta’sirida trayektoriyaga urinmaning pasayishiga aytiladi.",
            "O‘qning otish yo‘nalishidan orqaga aylanishi va shu bilan birgalikda o‘qning qarama qarshi harakati, havoning namligi va og‘irlik kuchi ta’siridan qo‘rol ufqiga urinmaning pasayishiga aytiladi.",
            "Nishonga to‘g‘rilangan qurol stvol kanali o‘qining davomi hisoblangan to‘g‘ri chiziq ko‘tarilish chizig‘iga aytiladi."
        ],
        "answer": 1
    },
    {
        "q": "O‘qlarning yoyilishi deb nimaga ataladi?",
        "options": [
            "Bir xil sharoitlarda faqat birgina quroldan otish paytidagi yoyilish hodisasiga aytiladi.",
            "Sharoiti bir xil va birgina quroldan otish paytidagi aylanish hodisasiga aytiladi.",
            "Boshlang‘ich tezliklarning har xilligiga aytiladi.",
            "Otish yo‘nalishini va irg‘itish burchaklarining har xilligiga aytiladi."
        ],
        "answer": 0
    },
    {
        "q": "Trayektoriya deb nimaga aytiladi?",
        "options": [
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Qurolning (granataning) muallaq uchish jarayonida yengilik markazida hosil bo‘ladigan to‘g‘ri chiziqqa aytiladi.",
            "O‘qning (granataning) havoda uchish jarayonida og‘irlik markazi hosil qiladigan egri chiziqqa aytiladi.",
            "Nishonga to‘g‘rilangan qurol stvol kanali o‘qining davomi hisoblangan to‘g‘ri chiziqqa aytiladi."
        ],
        "answer": 2
    },
    {
        "q": "Uchib chiqish nuqtasi deb nimaga ataladi?",
        "options": [
            "O‘q uchib chiqishi paytida stvol kanali o‘qining davomi hisoblanuvchi to‘g‘ri chiziq bo‘ylab irg‘itishga aytiladi.",
            "Nishonga to‘g‘rilangan qurol stvoli kanalidan o‘qning davomi hisoblangan to‘g‘ri chiziqqa aytiladi.",
            "Nishonga to‘g‘rilangan qurol (granatomet) stvoli kanalidan o‘q (granata)ning uchib chiqishi davomi hisoblangan to‘g‘ri chiziqqa aytiladi.",
            "Qurol stvoli og‘iz kesimining markaziga aytiladi."
        ],
        "answer": 3
    },
    {
        "q": "Havo qarshilik kuchining kattaligi nimaga bog‘liq?",
        "options": [
            "O‘q (granata)larning yoyilishi tasodifiy xatolarning normal qonuniga bo‘ysunadi, u esa o‘q (granata)lar yoyilishiga nisbatan yoyilish qonuni bo‘lib bog‘liq.",
            "O‘q (granata)larning yoyilishi aniq xatolarning normal qonuniga bo‘ysunadi, bu esa tashqi shartlarga bog‘liq.",
            "Havo qarshilik kuchining kattaligi o‘qning (granataning) uchish tezligiga, kalibriga va shakliga, hamda uning yuzasiga va havoning zichligiga bog‘liq.",
            "Bosim orqali havoning kuchini o‘rtachaligi o‘qning (granataning) uchish harakatiga bog‘liq."
        ],
        "answer": 2
    },
    {
        "q": "Ko‘tarilish chizig‘i deb nimaga aytiladi?",
        "options": [
            "Tushish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Tushish orqali o‘qning egri nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Nishonga to‘g‘rilangan qurol stvol kanali o‘qining davomi hisoblangan to‘g‘ri chiziqqa aytiladi."
        ],
        "answer": 3
    },
    {
        "q": "Otish tekisligi deb nimaga aytiladi?",
        "options": [
            "Tushish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Ko‘tarilish chizig‘i orqali o‘tuvchi vertikal tekislikka aytiladi.",
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Otilib chiqish nuqtasi orqali o‘tuvchi vertikal tekislikka aytiladi."
        ],
        "answer": 1
    },
    {
        "q": "Ko‘tarilish burchagi deb nimaga aytiladi?",
        "options": [
            "Irg‘itish chizig‘i bilan qurol ufqi (gorizonti) orasidagi burchakka aytiladi.",
            "Ko‘tarilish chizig‘i bilan o‘q (granata) yo‘nalishining ufqi (gorizonti) orasidagi masofaga aytiladi.",
            "Ko‘tarilish chizig‘i bilan qurol ufqi orasidagi burchakka aytiladi.",
            "Ko‘tarilish chizig‘i va irg‘itish chizig‘i orasidagi burchakka aytiladi."
        ],
        "answer": 2
    },
    {
        "q": "Irg‘itish chizig‘i deb nimaga aytiladi?",
        "options": [
            "O‘q uchib chiqishi paytida stvol kanali o‘qining davomi hisoblanuvchi to‘g‘ri chiziqqa aytiladi.",
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Tushish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Uchib chiqish nuqtasi orqali o‘tuvchi kesik gorizontal tekislikka aytiladi."
        ],
        "answer": 0
    },
    {
        "q": "Irg‘itish burchagi deb nimaga aytiladi?",
        "options": [
            "Tushish nuqtasi va irg‘itish burchagi orasidagi burchakka aytiladi.",
            "Ko‘tarilish chizig‘i va irg‘itish chizig‘i orasidagi burchakka aytiladi.",
            "Otilish chizig‘i bilan qurol ufqi orasidagi masofaga aytiladi.",
            "Irg‘itish chizig‘i bilan qurol ufqi (gorizonti) orasidagi burchakka aytiladi."
        ],
        "answer": 3
    },
    {
        "q": "Uchish burchagi deb nimaga aytiladi?",
        "options": [
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Tushish nuqtasi va irg‘itish burchagi orasidagi burchakka aytiladi.",
            "Ko‘tarilish chizig‘i va irg‘itish chizig‘i orasidagi burchakka aytiladi.",
            "Uchish nuqtasi orasidan o‘tuvchi gorizontal tekislikka aytiladi."
        ],
        "answer": 2
    },
    {
        "q": "Qurol ufqi (gorizonti) deb nimaga aytiladi?",
        "options": [
            "Tushish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi.",
            "Trayektoriyaning pastga qarab ketishiga aytiladi.",
            "Uchish nuqtasi orasidan o‘tuvchi gorizontal tekislikka aytiladi.",
            "Uchib chiqish nuqtasi orqali o‘tuvchi gorizontal tekislikka aytiladi."
        ],
        "answer": 3
    },
    {
        "q": "Tushish nuqtasi deb nimaga aytiladi?",
        "options": [
            "Tushish nuqtasida trayektoriyaga urinma va qurol gorizonti orasidagi burchagiga aytiladi.",
            "Tushish nuqtasi orqali o‘tuvchi urinma va qurol gorizonti orasidagi gorizontal tekislikka aytiladi.",
            "Trayektoriyaning qurol gorizonti bilan kesishgan nuqtasiga aytiladi.",
            "Trayektoriyaga urinma va qurol gorizonti orasidan pastga qarab ketishiga aytiladi."
        ],
        "answer": 1
    },
    {
        "q": "Patronlarning belgilari odatda ikkita sonli ko‘rsatkichlardan iborat: Masalan: 7.62 x 51. Bu nimalarni belgilaydi?",
        "options": [
            "O‘qning kalibri va gilzaning uzunligini.",
            "O‘qning kalibrini.",
            "O‘qning kalibri va o‘qning uzunligini.",
            "Zavod partiyasi va gilzaning qalinligini."
        ],
        "answer": 0
    },
    {
        "q": "Jangovar zaryad yonishida ajraladigan energiya qanday ishlarga sarflanadi:",
        "options": [
            "O‘qning ilgarilanma harakatlanishiga, stvol kanalida harakatlanishida ishqalanish ishini yengishga; qurolning ortga siltinishiga; stvolning qizishi va kengayishiga, gilza va o‘qning qizishiga.",
            "Snaryadni harakatlanishiga, stvol kanalida harakatlanishida ishqalanish ishini yengishga; qurolning ortga siltinishiga; stvolning qizishi va kengayishiga, gilza va o‘qning qizishiga.",
            "O‘qqa aylanma harakat berishga; stvol kanalida harakatlanishida ishqalanish ishini yengishga; qurolning ortga siltinishiga; stvolning qizishi va kengayishiga, gilza va o‘qning qizishiga.",
            "O‘qning ilgarilanma harakatlanishiga, o‘qqa aylanma harakat berishga; stvol kanalida harakatlanishida ishqalanish ishini yengishga; qurolning ortga siltinishiga; stvolning qizishi va kengayishiga, gilza va o‘qning qizishiga."
        ],
        "answer": 3
    },
    {
        "q": "O‘qning uchishiga qanday kuchlar ta’sir qiladi:",
        "options": [
            "Og‘irlik kuchi va yerni tortish kuchi.",
            "Havo qarshiligi va og‘irlik kuchi.",
            "Yerni tortish kuchi va havo qarshiligi.",
            "Havo qarshiligi va uyurma."
        ],
        "answer": 1
    },
    {
        "q": "O‘qning stvol kanalidan chiqib ketishi uchun yongan jangovar zaryadning qancha foizi ta’sir qiladi?",
        "options": [
            "40%",
            "50%",
            "45%",
            "35%"
        ],
        "answer": 3
    },
    {
        "q": "Ballistika deb nimaga aytiladi?",
        "options": [
            "Ballistika – stvol xarakati qonunlarini o‘rganuvchi fan. Ichki va tashqi ballistika tafovut etiladi.",
            "Ballistika – snaryad qoidasini qonunlarini o‘rganuvchi fan. Ichki va tashqi ballistika tafovut etiladi.",
            "Ballistika – snaryad (o‘q) harakati qonunlarini o‘rganuvchi fan. Ichki va tashqi ballistika tafovut etiladi.",
            "Ballistika – snaryad xarakati o‘rganuvchi fan. Ichki va tashqi ballistika tafovut etiladi."
        ],
        "answer": 2
    },
    {
        "q": "Ichki ballistika haqida ma’lumot:",
        "options": [
            "Ichki ballistika – bu stvol kanalida snaryadning porox gazlari ta’siridagi harakatini o‘rganuvchi harbiy-texnikaviy fandir.",
            "Ichki ballistika – bu stvol kanalida snaryadning porox gazlari ta’siridagi harakatini, shuningdek bu harakat bilan birga kechuvchi jarayonlarni o‘rganuvchi harbiy-texnikaviy fandir.",
            "Ichki ballistika – bu stvol kanalida porox gazlari ta’siridagi harakatini o‘rganuvchi fandir.",
            "Ichki ballistika – bu harakat bilan birga kechuvchi jarayonlarni o‘rganuvchi fandir."
        ],
        "answer": 1
    },
    {
        "q": "Otish ta’rifi:",
        "options": [
            "Otish – stvol kanalidan snaryadning otilish jarayonidir.",
            "Otish – bu porox gazlari ta’sirida stvol kanalidan snaryadning otilish jarayonidir. Qurol stvol kanalida tez yonish jarayoni otish deb ataladi.",
            "Otish – bu porox gazlari ta’sirida stvol kanalidan snaryad (o‘q)ning otilish jarayonidir. Qurol stvol kanalida jangovar porox zaryadining tez yonish jarayoni otish deb ataladi.",
            "Otish – bu jangovar porox otilish jarayonidir."
        ],
        "answer": 2
    },
    {
        "q": "Otishda ketma-ket keladigan quyidagi davrlar tafovut etiladi:",
        "options": [
            "Birinchi (asosiy) davr, ikkinchi davr, uchinchi davr.",
            "Dastlabki davr, ikkinchi davr, uchinchi davr.",
            "Dastlabki davr, birinchi (asosiy) davr, ikkinchi davr, uchinchi davr (gazlar ta’siridan keyingi davr).",
            "Dastlabki davr, ikkinchi davr, uchinchi davr."
        ],
        "answer": 2
    },
    {
        "q": "Otishning dastlabki davri qachongacha davom etadi?",
        "options": [
            "Snaryad harakatga kirishgan paytgacha davom etadi.",
            "Snaryad chiqa boshlagan paytdan snaryad harakatga kirishgan paytgacha davom etadi.",
            "Snaryad boshlagan paytdan harakat to‘xtatgan paytgacha davom etadi.",
            "Zaryad yona boshlagan paytdan snaryad harakatga kirishgan paytgacha davom etadi."
        ],
        "answer": 3
    },
    {
        "q": "Otishning birinchi (asosiy) davri:",
        "options": [
            "Snaryad harakatga kirishgan paytdan boshlanib, zaryad to‘la yonib tugagan paytda tamomlanadi.",
            "Zaryad to‘la yonib tugagan paytdan snaryad stvol kanalidan uchib chiqqan paytgacha davom etadi.",
            "Gazlar stvol kanalidan 1200-2000 m/s tezlikda chiqib ta’sir ko‘rsatadi.",
            "Snaryad stvol kanalidan uchib chiqqanda oladigan tezlikdir."
        ],
        "answer": 0
    },
    {
        "q": "Otishning ikkinchi davri:",
        "options": [
            "Gazlar stvol kanalidan 1200-2000 m/s tezlikda chiqadigan davr.",
            "Snaryad stvol kanalidan uchib chiqqanda oladigan tezlik.",
            "Snaryad harakatga kirishgan paytdan boshlanadigan davr.",
            "Zaryad to‘la yonib tugagan paytdan snaryad stvol kanalidan uchib chiqqan paytgacha davom etadi."
        ],
        "answer": 3
    },
    {
        "q": "Otishning uchinchi davrida:",
        "options": [
            "Snaryad stvol kanalidan uchib chiqqanda oladigan tezlik hosil bo‘ladi.",
            "Gazlar stvol kanalidan 1200-2000 m/s va bundan katta tezlikda chiqib, snaryadga ta’sir ko‘rsatishda davom etadi.",
            "Snaryad harakatga kirishgan paytdan boshlanadi.",
            "Zaryad to‘la yonib tugagan paytda tamomlanadi."
        ],
        "answer": 1
    },
    {
        "q": "O‘qning boshlang‘ich tezligi:",
        "options": [
            "Qurolning tepish kuchi ta’sirida orqaga urishi.",
            "Stvolning ballistik xususiyatlarini saqlash darajasi.",
            "Snaryad (o‘q)ning stvol kanalidan uchib chiqqanda oladigan tezligidir.",
            "Zaryad to‘la yonib tugagan paytdan boshlab olingan tezlik."
        ],
        "answer": 2
    },
    {
        "q": "Qurolning tepinishi bu:",
        "options": [
            "Qurolning tepish kuchi ta’sirida oldiga urishi.",
            "Qurolning tepish kuchi ta’sirida stvolning qizishi.",
            "Qurolning tepish kuchi ta’sirida yon tomonga surilishi.",
            "Qurolning (to‘pda – tepuvchi qismlarning) tepish kuchi ta’sirida orqaga urishi (orqaga siltanishi)."
        ],
        "answer": 3
    },
    {
        "q": "Stvolning yashovchanligi nima?",
        "options": [
            "Qurol stvoli o‘zining ballistik xususiyatlarini yo‘qotgunga qadar undan otish mumkin bo‘lgan o‘qlarning eng yuqori miqdoridir.",
            "Stvolning tashqi kuchlarga bardosh berishi.",
            "Stvolning metall qattiqligi darajasi.",
            "Stvolning maksimal bosimga bardosh berishi."
        ],
        "answer": 0
    },
    {
        "q": "«Minglik» burchak o‘lchov birligi ta’rifi:",
        "options": [
            "Aylananing 1/6000 ulushiga teng bo‘lgan yoyga tayangan markaziy burchak «minglik» deyiladi.",
            "Aylananing 1/1000 ulushiga teng bo‘lgan yoyga tayangan markaziy burchak «minglik» deyiladi.",
            "Aylananing 1/6000 ulushiga yoki radiusning 1/1000 ulushiga teng bo‘lgan yoyga yotgan burchak.",
            "Aylananing 1/6000 ulushiga yoki radiusning 1/1000 ulushiga teng bo‘lgan yoyga tayangan markaziy burchak «minglik» deyiladi."
        ],
        "answer": 3
    },
    {
        "q": "Tashqi ballistika ta’rifi:",
        "options": [
            "Snaryadning uchish paytidagi og‘irlik markazini tavsiflovchi chiziq.",
            "Stvol harakati qonunlarini o‘rganuvchi fan.",
            "Snaryadga (o‘qqa) porox gazlari ta’siri to‘xtagan paytdan boshlab uning fazodagi harakati to‘g‘risidagi fandir.",
            "Stvol kanalida snaryadning harakatini o‘rganuvchi fandir."
        ],
        "answer": 2
    },
    {
        "q": "Trayektoriyaning asosiy elementlari:",
        "options": [
            "Snaryad uchishining to‘liq gorizontal uzoqligi, trayektoriya balandligi va to‘liq vaqti.",
            "Stvol harakati qonunlari va yoyilish koeffitsiyenti.",
            "Snaryadning uchish paytidagi og‘irlik markazi egri chizig‘i.",
            "O‘qning aylanish tezligi va havo qarshiligi."
        ],
        "answer": 0
    },
    {
        "q": "Yer bag‘irlab ketgan trayektoriya deb qanday trayektoriyalarga aytiladi?",
        "options": [
            "θ > 90° burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ < 40° burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ < 50° burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ < 45° (eng katta otish uzoqligi burchagidan kichik) burchaklarda hosil bo‘lgan trayektoriyalar."
        ],
        "answer": 3
    },
    {
        "q": "Osma trayektoriya deb qanday trayektoriyalarga aytiladi?",
        "options": [
            "θ < 45° burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ > 45° (eng katta otish uzoqligi burchagidan katta) burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ < 40° burchaklarda hosil bo‘lgan trayektoriyalar.",
            "θ < 50° burchaklarda hosil bo‘lgan trayektoriyalar."
        ],
        "answer": 1
    },
    {
        "q": "Tutash trayektoriyalar deb qanday trayektoriyalarga aytiladi?",
        "options": [
            "Har xil otish uzoqligini ta’minlovchi yer bag‘irlab ketgan trayektoriyalar.",
            "Bir xil otish uzoqligini beruvchi faqat yer bag‘irlab ketgan trayektoriyalar.",
            "Bir xil otish uzoqligini ta’minlovchi yer bag‘irlab ketgan va osma trayektoriyalar.",
            "Burchaklari bir xil bo‘lgan trayektoriyalar."
        ],
        "answer": 2
    },
    {
        "q": "Otish sharoitlari qaysi guruhlarga bo‘linadi?",
        "options": [
            "Meteorologiya sharoitlari, ballistika sharoitlari, topografiya sharoitlari.",
            "Atmosfera bosimi, havo harorati, shamol yo‘nalishi.",
            "Zaryad harorati, snaryadning boshlang‘ich tezligi, snaryadning og‘irligi.",
            "Fizik, kimyoviy va biologik sharoitlar."
        ],
        "answer": 0
    },
    {
        "q": "Meteorologiya sharoitlariga nimalar kiradi?",
        "options": [
            "Meteorologiya, ballistika va topografiya sharoitlari.",
            "Atmosfera bosimi, havo harorati, shamolning yo‘nalishi va tezligi, havo namligi.",
            "Zaryad harorati, boshlang‘ich tezlik va o‘q og‘irligi.",
            "Nishon balandligi va marshrut burchagi."
        ],
        "answer": 1
    },
    {
        "q": "Ballistika sharoitlariga nimalar kiradi?",
        "options": [
            "Atmosfera bosimi, havo harorati, shamol yo‘nalishi.",
            "Meteorologiya va topografiya sharoitlari.",
            "Zaryad harorati, snaryadning boshlang‘ich tezligi, snaryadning og‘irligi va shakli.",
            "Nishon joylashgan burchagi va qiyalik."
        ],
        "answer": 2
    },
    {
        "q": "Topografiya sharoitlariga nimalar kiradi?",
        "options": [
            "Nishon joylashgan joyining burchagi, mashinaning yonlama qiyaligi.",
            "Ballistika va meteorologiya sharoitlari.",
            "Shamolning yo‘nalishi va tezligi, havo namligi.",
            "Zaryadning namligi va saqlanish muddati."
        ],
        "answer": 0
    },
    {
        "q": "Sochilish hodisasi bu:",
        "options": [
            "Har xil quroldan deyarli bir xil shart-sharoitlarda otishda snaryadlarning tarqalishi.",
            "Bitta quroldan deyarli har xil shart-sharoitlarda otishda snaryadlarning tarqalishi.",
            "Bitta quroldan deyarli bir xil shart-sharoitlarda portlatishda snaryadlarning tarqalishi.",
            "Bitta quroldan deyarli bir xil shart-sharoitlarda otishda snaryadlarning har yoqqa tarqalish hodisasi."
        ],
        "answer": 3
    },
    {
        "q": "Sochilish sabablariga nimalar kiradi?",
        "options": [
            "Boshlang‘ich tezliklar har xil bo‘lishi, irg‘itish burchaklari va otish yo‘nalishi har xil bo‘lishi, snaryadlarning havoda uchish sharoitlari har xil bo‘lishi.",
            "Boshlang‘ich tezliklarning bir xilligi va nishon o‘lchami.",
            "Faqat shamol yo‘nalishi va havo haroratining o‘zgarishi.",
            "Qurolning vazni va otuvchining holati."
        ],
        "answer": 0
    },
    {
        "q": "To‘g‘ri navodka bilan o‘t ochishda:",
        "options": [
            "Trayektoriya mo‘ljallash chizig‘idan nishondan balandga ko‘tarilmaydi.",
            "Trayektoriya mo‘ljalga olish chizig‘i nishondan balandga ko‘tarilmaydi.",
            "Trayektoriya mo‘ljalga olish nishondan balandga ko‘tarilmaydi.",
            "Trayektoriya gorizontga parallel harakatlanadi."
        ],
        "answer": 1
    },
    {
        "q": "Jangda kuzatuv va nishon ko‘rsatish nima maqsadda olib boriladi?",
        "options": [
            "Jangda kuzatuv o‘z vaqtida dushmanni topish va uning ta’sir qilish xususiyatini aniqlash, komandirlar signali, qo‘shinlar harakati va otish natijalarini kuzatish maqsadida olib boriladi.",
            "Faqat dushmanning joylashuv o‘rnini xaritaga tushirish uchun.",
            "Faqat otilgan o‘qlar sonini hisoblash uchun.",
            "Faqat qo‘shni bo‘linmalarning harakatini nazorat qilish uchun."
        ],
        "answer": 0
    },
    {
        "q": "Dastlabki o‘rnatma tayinlash nima?",
        "options": [
            "Dastlabki o‘rnatma deb to‘pdan/quroldan birinchi o‘qni otish (pulemyotdan birinchi navbatni) uchun aniqlangan o‘rnatmaga aytiladi.",
            "Barcha o‘qlarni otish uchun umumiy o‘rnatmaga aytiladi.",
            "Otish yakunlangandan keyingi ko‘rsatkichlarga aytiladi.",
            "Qurolni tozalash rejimiga aytiladi."
        ],
        "answer": 0
    },
    {
        "q": "Zabt etiladigan maydon nima?",
        "options": [
            "Trayektoriyaning pastga qarab ketuvchi bo‘g‘ini nishon balandligidan oshmaydigan joy oralig‘i.",
            "O‘q teshmaydigan yashirinish joyining orqasidagi maydon.",
            "Yopiq maydonning mazkur trayektoriyasidan nishon zararlanishi mumkin bo‘lmagan qismi.",
            "Qurolning maksimal otish uzoqligi maydoni."
        ],
        "answer": 0
    },
    {
        "q": "Yopiq maydon nima?",
        "options": [
            "Trayektoriyaning pastga qarab ketuvchi bo‘g‘ini nishon balandligidan oshmaydigan joy oralig‘i.",
            "O‘q teshmaydigan yashirinish joyining orqasidagi, uning qirrasidan uchrashish nuqtasigacha cho‘zilgan maydon.",
            "Yopiq maydonning mazkur trayektoriyasidan nishon zararlanishi mumkin bo‘lmagan qismi.",
            "Qurol ko‘rinmaydigan joy."
        ],
        "answer": 1
    },
    {
        "q": "Qo‘zg‘almas (zararlantirilmaydigan) maydon nima?",
        "options": [
            "Trayektoriyaning pastga qarab ketuvchi bo‘g‘ini nishon balandligidan oshmaydigan maydon.",
            "O‘q teshmaydigan yashirinish joyi maydoni.",
            "Yopiq maydonning mazkur trayektoriyasidan nishon zararlanishi mumkin bo‘lmagan qismi.",
            "O‘q yetib bormaydigan maksimal chegara."
        ],
        "answer": 2
    },
    {
        "q": "Stvolning mustahkamligi bu:",
        "options": [
            "Stvol devorlari metallining o‘q bosimiga chidamliligi.",
            "Stvol devorlari metallining porox gazlari yurishiga chidamliligi.",
            "Stvol devorlari metallining porox gazlari bosimiga chidamliligi.",
            "Stvolning tashqi zarbalarga chidamliligi."
        ],
        "answer": 2
    },
    {
        "q": "Otish kursining mo‘ljallanishini ayting:",
        "options": [
            "Otish kursi muddatli harbiy xizmatchilar, SER xizmatchilari, HTM kursantlari va kontrakt harbiy xizmatchilariga qurol-aslahalarni mohirona va samarali qo‘llashni o‘rgatish uchun mo‘ljallangan.",
            "Faqat muddatli harbiy xizmatchilarni tayyorlash uchun mo‘ljallangan.",
            "Faqat HTM kursantlariga dars berish uchun mo‘ljallangan.",
            "Barcha harbiy qismlarda umumiy xavfsizlikni ta’minlash uchun."
        ],
        "answer": 0
    },
    {
        "q": "Mashqni bajarganlik uchun belgilanadigan baho qaysi hollarda bir ballga pasaytiriladi?",
        "options": [
            "Jangovar mashina qurollaridan otishda umumiy vaqt 10 soniyadan oshmaganda, birinchi o‘q uzish kechikib amalga oshirilganda yoki ko‘rsatilgan nishonlardan biri o‘qqa tutilmagan bo‘lsa.",
            "Agar o‘q uzish 1 daqiqaga kechiksa.",
            "Agar o‘rganuvchi noto‘g‘ri kiyingan bo‘lsa.",
            "Agar otish mashg‘ulotiga 5 daqiqa kechikib kelinsa."
        ],
        "answer": 0
    },
    {
        "q": "Quruqlikdagi qo‘shinlar o‘q otar qurollar, jangovar mashinalar va tanklardan otish kursi qaysi buyruqqa asosan tasdiqlangan?",
        "options": [
            "O‘zR MVning 2020 yil 29 avgustdagi 560-sonli buyrug‘i",
            "O‘zR MVning 2022 yil 2 maydagi 259-sonli buyrug‘i",
            "O‘zR MVning 2022 yil 19 apreldagi 320-sonli buyrug‘i",
            "O‘zR MVning 2023 yil 2 maydagi 375-sonli buyrug‘i"
        ],
        "answer": 3
    },
    {
        "q": "Nishonlarni kuzatuv bilan razvedka qilish va nishon ko‘rsatishga oid mashqlar qaysi buyruqda belgilab o‘tilgan?",
        "options": [
            "O‘zR MVning 2014 yil 20 iyundagi 424-sonli buyrug‘ida.",
            "O‘zR MVning 2023 yil 2 maydagi 375-sonli buyrug‘ida.",
            "O‘zR MVning 2020 yil 30 avgustdagi 650-sonli buyrug‘ida.",
            "O‘zR MVning 2022 yil 15 yanvardagi 110-sonli buyrug‘ida."
        ],
        "answer": 1
    },
    {
        "q": "Otish maydonida dastlabki marra bilan o‘t ochish marrasi orasidagi masofa (o‘qotar qurollar uchun):",
        "options": [
            "Kamida 8 m.",
            "Kamida 15 m.",
            "Kamida 10 m.",
            "Kamida 20 m."
        ],
        "answer": 2
    },
    {
        "q": "Bo‘linmalar otish maydoniga mashg‘ulot boshlanishidan necha daqiqa oldin yetib kelishi kerak?",
        "options": [
            "45 daqiqa.",
            "30 daqiqa.",
            "60 daqiqa.",
            "15 daqiqa."
        ],
        "answer": 1
    },
    {
        "q": "Qaysi hollarda yo‘q qilingan nishonlar sonidan qat’iy nazar, otish mashg‘uloti “qoniqarsiz” deb baholanadi?",
        "options": [
            "Umumiy vaqtdan 10 soniyadan ko‘p oshirilsa, to‘xtash marrasidan keyin o‘q uzilsa yoki xavfsizlik choralari qo‘pol ravishda buzilsa.",
            "Nishonga faqat bitta o‘q tekkanda.",
            "Mashq 5 soniya tezroq bajarilganda.",
            "Komanda ovozi eshitilmay qolganda."
        ],
        "answer": 0
    },
    {
        "q": "Jangovar texnikalardan harakat davomida qisqa to‘xtab otish vaqtlari (kunduzi va tunda):",
        "options": [
            "Kunduzi – 10 soniya, tunda – 12 soniya.",
            "Kunduzi – 12 soniya, tunda – 15 soniya.",
            "Kunduzi – 15 soniya, tunda – 20 soniya.",
            "Kunduzi – 8 soniya, tunda – 10 soniya."
        ],
        "answer": 0
    },
    {
        "q": "Paydo bo‘luvchi va harakatchan sun’iy nishonlar variantlar soni:",
        "options": [
            "Kunduz kuni uchta, tungi vaqtda ikkita.",
            "Kunduz kuni uchta, tungi vaqtda uchta.",
            "Kunduz kuni to‘rtta, tungi vaqtda ikkita.",
            "Kunduz kuni ikkita, tungi vaqtda bitta."
        ],
        "answer": 0
    },
    {
        "q": "Harakat davomida qisqa to‘xtashlarning davomiyligi:",
        "options": [
            "Kunduzi ko‘pi bilan 7 soniyadan, tunda 9 soniyadan oshmasligi kerak.",
            "Kunduzi 7 soniyadan, tunda 10 soniyadan oshmasligi kerak.",
            "Kunduzi 8 soniyadan, tunda 10 soniyadan oshmasligi kerak.",
            "Kunduzi 10 soniyadan, tunda 15 soniyadan oshmasligi kerak."
        ],
        "answer": 0
    },
    {
        "q": "Otish mashg‘uloti oldidan rahbar bo‘linma komandiriga qanday vazifa belgilab beradi?",
        "options": [
            "Mo‘ljalni ko‘rsatadi, dushman va qo‘shnilar haqidagi ma’lumotlarni, asosiy va xavfli yo‘nalishlarni aytadi, pozitsiya marralari va shay holatga kelish vaqtini belgilaydi.",
            "Faqat o‘q-dori sonini aytadi.",
            "Faqat nishon masofasini ko‘rsatadi.",
            "Faqat saf tortish buyrug‘ini beradi."
        ],
        "answer": 0
    },
    {
        "q": "Ichki ballistika fani nimani o‘rganadi?",
        "options": [
            "O‘qning porox gazlari ta’siri tugagandan keyingi harakatlarini.",
            "Otish paytida hosil bo‘ladigan jarayonlarni, xususan o‘q (granata)ning stvol kanalida harakatlanishini.",
            "O‘qlarning havoda uchish qonunlarini.",
            "Nishonlarning zararlanish darajasini."
        ],
        "answer": 1
    },
    {
        "q": "AK-74 avtomatining mo‘ljallab otish uzoqligi qancha?",
        "options": [
            "800 m.",
            "1000 m.",
            "1100 m.",
            "1200 m."
        ],
        "answer": 1
    },
    {
        "q": "Traektoriya nima?",
        "options": [
            "Uchib chiqish nuqtasi gorizonti.",
            "Qurolning optik o‘qi.",
            "O‘qning havoda uchish jarayonida og‘irlik markazi hosil qiladigan egri chiziq.",
            "Mo‘ljal chizig‘i."
        ],
        "answer": 2
    }
]

# =========================================================
# FOYDALANUVCHILAR SESSIYASI
# =========================================================

users = {}

def get_progress_bar(total_time, remaining_time):
    """Vizual vaqt shkalasi"""
    total_blocks = 10
    filled_blocks = int((remaining_time / total_time) * total_blocks)
    empty_blocks = total_blocks - filled_blocks
    if remaining_time > 30:
        bar = "🟩" * filled_blocks + "⬜" * empty_blocks
    elif remaining_time > 15:
        bar = "🟨" * filled_blocks + "⬜" * empty_blocks
    else:
        bar = "🟥" * filled_blocks + "⬜" * empty_blocks
    return bar

# =========================================================
# /start BUYRUG'I
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 TESTNI BOSHLASH",
                callback_data="start_test"
            )
        ]
    ]

    total_q = len(questions)

    text = (
        "🎖 <b>OTISH TAYYORGARLIGI FANIDAN TEST</b>\n\n"
        f"👨‍🏫 <b>Muallif:</b> <i>{AUTHOR_NAME}</i>\n\n"
        f"📊 <b>Savollar soni:</b> {total_q} ta\n"
        f"⏱ <b>Har bir savolga:</b> 60 soniya (jonli taymer)\n"
        f"🔀 <b>Savollar tartibi:</b> Tasodifiy (Random)\n\n"
        "<b>Baholash mezonlari:</b>\n"
        "• <b>5 (A'lo)</b> — 90% va undan yuqori\n"
        "• <b>4 (Yaxshi)</b> — 80% – 89%\n"
        "• <b>3 (Qoniqarli)</b> — 70% – 79%\n"
        "• <b>2 (Qoniqarsiz)</b> — 70% dan past\n\n"
        f"👤 <b>Ishtirokchi:</b> {user.full_name}\n\n"
        "Tayyor bo‘lsangiz, quyidagi tugmani bosing:"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# =========================================================
# ADMIN UCHUN /stat BUYRUG'I
# =========================================================

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ADMIN_ID != 0 and user_id != ADMIN_ID:
        return

    if not history_records:
        await update.message.reply_text("📋 Hozircha hech kim test topshirmadi.")
        return

    report = f"📊 <b>UMUMIY NATIJALAR ({len(history_records)} ta urinish):</b>\n\n"
    for i, r in enumerate(history_records[-30:], 1):  # Oxirgi 30 ta natija
        report += (
            f"{i}. <b>{r['name']}</b> ({r['username']})\n"
            f"   Natija: {r['correct']}/{r['total']} ({r['percent']:.1f}%) — <b>{r['grade']}</b>\n"
        )

    await update.message.reply_text(report, parse_mode="HTML")

# =========================================================
# TESTNI BOSHLASH
# =========================================================

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_fullname = query.from_user.full_name
    username = f"@{query.from_user.username}" if query.from_user.username else "yo'q"

    question_order = list(range(len(questions)))
    random.shuffle(question_order)

    users[user_id] = {
        "name": user_fullname,
        "username": username,
        "question": 0,
        "correct": 0,
        "answers": [],
        "question_order": question_order,
        "message_id": query.message.message_id,
        "chat_id": query.message.chat_id,
        "is_finished": False
    }

    # Admin'ga xabar berish
    if ADMIN_ID != 0:
        try:
            admin_msg = (
                f"🟢 <b>Yangi ishtirokchi test boshladi!</b>\n\n"
                f"👤 <b>Ism:</b> {user_fullname}\n"
                f"🔗 <b>Username:</b> {username}\n"
                f"🆔 <b>ID:</b> <code>{user_id}</code>"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="HTML")
        except Exception:
            pass

    await send_question(query, user_id, context)

# =========================================================
# SAVOLNI YUBORISH
# =========================================================

def get_question_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🅰️ A", callback_data="answer_0"),
            InlineKeyboardButton("🅱️ B", callback_data="answer_1")
        ],
        [
            InlineKeyboardButton("©️ C", callback_data="answer_2"),
            InlineKeyboardButton("🇩 D", callback_data="answer_3")
        ],
        [
            InlineKeyboardButton("🛑 Testni yakunlash", callback_data="stop_test")
        ]
    ])

async def send_question(query, user_id, context: ContextTypes.DEFAULT_TYPE):
    if user_id not in users:
        return

    data = users[user_id]
    number = data["question"]

    if number >= len(data["question_order"]):
        await finish_test(query, user_id, context=context)
        return

    question_index = data["question_order"][number]
    question = questions[question_index]

    letters = ["A", "B", "C", "D"]

    text = (
        f"📝 <b>SAVOL {number + 1} / {len(data['question_order'])}</b>\n\n"
        f"<b>{question['q']}</b>\n\n"
    )

    for i, option in enumerate(question["options"]):
        lbl = letters[i] if i < len(letters) else str(i + 1)
        text += f"<b>{lbl})</b> {option}\n\n"

    bar = get_progress_bar(60, 60)
    text += f"⏳ <b>Vaqt:</b> {bar} <code>60 soniya</code>"

    keyboard = get_question_keyboard()

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    bot_instance = context.bot if context else query.get_bot()

    # Jonli taymer
    asyncio.create_task(
        question_timer(
            bot_instance,
            data["chat_id"],
            data["message_id"],
            user_id,
            number,
            question,
            query,
            context
        )
    )

# =========================================================
# 60 SONIYALIK JONLI TAYMER
# =========================================================

async def question_timer(bot, chat_id, message_id, user_id, question_number, question_obj, query, context):
    letters = ["A", "B", "C", "D"]
    keyboard = get_question_keyboard()

    total_time = 60
    step = 5

    try:
        for remaining in range(total_time - step, 0, -step):
            await asyncio.sleep(step)

            if user_id not in users or users[user_id]["question"] != question_number or users[user_id].get("is_finished"):
                return

            bar = get_progress_bar(total_time, remaining)

            text = (
                f"📝 <b>SAVOL {question_number + 1} / {len(users[user_id]['question_order'])}</b>\n\n"
                f"<b>{question_obj['q']}</b>\n\n"
            )
            for i, option in enumerate(question_obj["options"]):
                lbl = letters[i] if i < len(letters) else str(i + 1)
                text += f"<b>{lbl})</b> {option}\n\n"

            text += f"⏳ <b>Vaqt:</b> {bar} <code>{remaining:02d} soniya</code>"

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        await asyncio.sleep(step)

        if user_id not in users or users[user_id]["question"] != question_number or users[user_id].get("is_finished"):
            return

        users[user_id]["question"] += 1

        if users[user_id]["question"] >= len(users[user_id]["question_order"]):
            await finish_test(query, user_id, context=context)
        else:
            await query.edit_message_text(
                f"⏰ <b>{question_number + 1}-savol uchun 60 soniya vaqt tugadi!</b>\n\n"
                f"❌ <i>Javob hisoblanmadi.</i>\n\n"
                f"➡️ Keyingi savolga o‘tilmoqda...",
                parse_mode="HTML"
            )
            await asyncio.sleep(1.5)
            await send_question(query, user_id, context)

    except asyncio.CancelledError:
        pass
    except Exception:
        pass

# =========================================================
# JAVOBNI QABUL QILISH
# =========================================================

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in users or users[user_id].get("is_finished"):
        await query.edit_message_text(
            "❗ Test sessiyasi yakunlangan.\n\n/start buyrug‘i orqali qaytadan boshlang."
        )
        return

    data = users[user_id]
    number = data["question"]

    if number >= len(data["question_order"]):
        await finish_test(query, user_id, context=context)
        return

    selected = int(query.data.split("_")[1])
    question_index = data["question_order"][number]
    question = questions[question_index]

    data["answers"].append(selected)

    if selected == question["answer"]:
        data["correct"] += 1

    data["question"] += 1

    if data["question"] >= len(data["question_order"]):
        await finish_test(query, user_id, context=context)
    else:
        await send_question(query, user_id, context)

# =========================================================
# TESTNI MUDDATIDAN OLDIN YAKUNLASH
# =========================================================

async def stop_test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Test to‘xtatildi!", show_alert=False)

    user_id = query.from_user.id
    if user_id in users:
        await finish_test(query, user_id, is_stopped_early=True, context=context)

# =========================================================
# TEST YAKUNI VA BAHOLASH
# =========================================================

async def finish_test(query, user_id, is_stopped_early=False, context: ContextTypes.DEFAULT_TYPE = None):
    if user_id not in users:
        return

    data = users[user_id]
    data["is_finished"] = True

    attempted = data["question"]
    total = len(data["question_order"])
    correct = data["correct"]
    
    evaluated_total = attempted if is_stopped_early and attempted > 0 else total
    wrong = evaluated_total - correct
    percent = (correct / evaluated_total) * 100 if evaluated_total > 0 else 0

    if percent >= 90:
        grade = "5 — A’LO"
    elif percent >= 80:
        grade = "4 — YAXSHI"
    elif percent >= 70:
        grade = "3 — QONIQARLI"
    else:
        grade = "2 — QONIQARSIZ"

    # Tarixga qo'shish
    history_records.append({
        "name": data["name"],
        "username": data["username"],
        "user_id": user_id,
        "correct": correct,
        "total": evaluated_total,
        "percent": percent,
        "grade": grade
    })

    # Admin'ga yakuniy hisobotni yuborish
    if ADMIN_ID != 0:
        try:
            bot_obj = context.bot if context else query.get_bot()
            stop_note = " (🛑 Muddatidan oldin to'xtatildi)" if is_stopped_early else ""
            report = (
                f"🏁 <b>Test yakunlandi!{stop_note}</b>\n\n"
                f"👤 <b>Ism:</b> {data['name']}\n"
                f"🔗 <b>Username:</b> {data['username']}\n"
                f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                f"📊 <b>Savollar:</b> {attempted} / {total}\n"
                f"✅ <b>To‘g‘ri javoblar:</b> {correct} ta\n"
                f"❌ <b>Xatolar:</b> {wrong} ta\n"
                f"📈 <b>Natija:</b> {percent:.1f}%\n"
                f"🎓 <b>Bahosi:</b> <b>{grade}</b>"
            )
            await bot_obj.send_message(chat_id=ADMIN_ID, text=report, parse_mode="HTML")
        except Exception:
            pass

    status_header = "🛑 <b>TEST MUDDATIDAN OLDIN TO‘XTATILDI!</b>" if is_stopped_early else "🏁 <b>TEST TO‘LIQ YAKUNLANDI!</b>"

    text = (
        f"{status_header}\n\n"
        f"👨‍🏫 <b>Muallif:</b> <i>{AUTHOR_NAME}</i>\n\n"
        f"👤 <b>Ishtirokchi:</b> {data['name']}\n"
        f"📊 <b>Ishlangan savollar:</b> {attempted} / {total}\n"
        f"✅ <b>To‘g‘ri javoblar:</b> {correct} ta\n"
        f"❌ <b>Noto‘g‘ri / o‘tkazilgan:</b> {wrong} ta\n"
        f"📈 <b>Samaradorlik:</b> {percent:.1f}%\n"
        f"🎓 <b>Bahosi:</b> <b>{grade}</b>\n\n"
        "Sinovda ishtirok etganingiz uchun rahmat! 👏"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 QAYTA TOPSHIRISH",
                callback_data="start_test"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# =========================================================
# RENDER UCHUN DOIMIY ISHLASH TIZIMI (WEB SERVER)
# =========================================================

async def handle_ping(request):
    return web.Response(text="Bot faol ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# =========================================================
# BOTNI ISHGA TUSHIRISH (Python 3.14+ moslashuvi)
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def run_bot():
    print("====================================")
    print("🤖 TELEGRAM TEST BOT ISHGA TUSHMOQDA")
    print(f"👨‍🏫 Muallif: {AUTHOR_NAME}")
    print(f"📚 Savollar soni: {len(questions)} ta")
    print("⏱ Har bir savol: 60 soniya (jonli taymer)")
    print("🛑 Istalgan vaqtda to‘xtatish imkoniyati mavjud")
    print("====================================")

    # Render serveri to'xtab qolmasligi uchun veb-serverni ishga tushirish
    await start_web_server()

    # Telegram Bot dasturi
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stat", stat_command))
    app.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(stop_test_handler, pattern="^stop_test$"))
    app.add_handler(CallbackQueryHandler(answer_question, pattern="^answer_[0-3]$"))

    # Botni ishga tushirish (async loop)
    async with app:
        await app.start()
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
