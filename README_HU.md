<img src="https://github.com/szmate00/hotspot_detection/blob/master/figures/logok_hu.png" height="150" />


# Lokális plazma-fal kölcsönhatások észlelése az EDICAM kamerarendszer által kinyert adatokban
Tudományos Diákköri Konferencia dolgozat

## Eötvös Loránd Tudományegyetem 2020
### Szerző: Szűcs Máté<br>
Fizika BSc II. évfolyam<br>

### Témavezető: Szepesi Tamás, Phd<br>

Energiatudományi Kutatóközpont, Fúziós Plazmafizika Laboratórium


## Absztrakt
A Napunkban végbemenő fúziós folyamatoknak köszönhetően van élet a Földön. Az emberekben több, mint fél évszázada ötlött fel a gondolat, hogy a Napban lejátszódó folyamatot a Földön végrehajtva fel lehetne használni közvetlen energiatermelésre. Hogy eljussunk a jól működő fúziós reaktorokig, nagyon fontos a berendezés védelme, hiszen, ha ez károsodik akkor leáll a fúzió.
Ilyen károsító jelenségek lehetnek a lokális plazma-fal kölcsönhatások (hotspotok).

A két legfejlettebb fajtája a mágneses összetartású fúziós berendezéseknek a tokamak és a sztellarátor. A németországi Wendelstein 7-X-et  a sztellarátor koncepció egyik főpróbájának is nevezhetjük, hiszen ez az eddigi legnagyobb és legambíciózusabb ilyen berendezés ami valaha épült. Munkám során kifejlesztettem egy algoritmust amely képes érzékelni e sztellarátornak a videodiagnosztikájául szolgáló EDICAM kamerarendszer képeiben a lokális hotspotokat. Az algoritmus 97.08%-os szenzitivitást ért el és a lokálisan kialakult hotspotok csak körülbelül 3%-át tévesztette el a tesztelés során. A kimenetül szolgáló három grafikon segítségével időben végigkövethetjük a plazmakisülések (lövések) adott területén esetleg fellépő hotspotok intenzitását, méretét és lecsengését, valamint akár a manipulátor helyzetét is. Az algoritmus jelentősen megkönnyíti a lövések utólagos kiértékelését, az első verziók által nyert adatokat már használják a Wendelstein 7-X német munkatársai is.


*(Megjegyzés: A kód angol nyelvű kommenteket tartalmaz.)*
