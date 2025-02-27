document.addEventListener("DOMContentLoaded", () => {
  let vybranaPole = [];
  let slovaKNajiti;
  let nalezenaSlova = [];
  let casZbyva = 60; // Výchozí čas, bude přepisován
  let timer;
  let table;
  let poziceSlov;
  let wordMeanings = {}; // Cache for meanings

  // Function to fetch meaning using crawl4ai
  async function fetchMeaning(word) {
    try {
      const response = await fetch(`/meaning?word=${encodeURIComponent(word)}`);
      if (response.ok) {
        const meaning = await response.text();
        return meaning.trim() || "Meaning not found";
      }
      return "Meaning not found";
    } catch (error) {
      console.error(`Error fetching meaning for ${word}:`, error);
      return "Meaning not found";
    }
  }

  // Preload meanings for all words before starting the game
  async function preloadMeanings(words) {
    const meaningPromises = words.map((word) => fetchMeaning(word));
    const meanings = await Promise.all(meaningPromises);
    words.forEach((word, index) => {
      wordMeanings[word] = meanings[index];
    });
  }

  window.spustitHru = async function () {
    const velikost = parseInt(document.getElementById("velikost").value);
    const pocetSlov = document.getElementById("pocet_slov").value;
    document.getElementById("hra").style.display = "block";
    document.getElementById("mrizka").innerHTML = "";
    document.getElementById("vysledek").innerHTML = "";
    nalezenaSlova = [];
    vybranaPole = [];

    // Set time based on grid size
    if (velikost === 10) casZbyva = 60;
    else if (velikost === 15) casZbyva = 80;
    else if (velikost === 20) casZbyva = 100;
    else if (velikost === 25) casZbyva = 120;
    else if (velikost === 30) casZbyva = 140;
    else if (velikost === 40) casZbyva = 180;
    else if (velikost === 50) casZbyva = 220;

    document.getElementById("cas").textContent = casZbyva;

    // Preload meanings before loading the grid
    try {
      const response = await fetch(
        `/mrizka?velikost=${velikost}&pocet_slov=${pocetSlov}`
      );
      const data = await response.json();
      slovaKNajiti = data.slova;
      poziceSlov = data.pozice || {};

      // Preload meanings for all words
      await preloadMeanings(slovaKNajiti);

      // Display words with tooltips
      const slovaContainer = document.getElementById("slova");
      slovaContainer.innerHTML = slovaKNajiti
        .map(
          (word) => `
              <span class="tooltip" data-word="${word}">
                  ${word}
                  <span class="tooltiptext">${
                    wordMeanings[word] || "Loading..."
                  }</span>
              </span>
          `
        )
        .join(", ");

      table = document.getElementById("mrizka");
      table.style.pointerEvents = "auto";
      data.mrizka.forEach((radek, i) => {
        const tr = document.createElement("tr");
        radek.forEach((pismeno, j) => {
          const td = document.createElement("td");
          td.textContent = pismeno;
          td.dataset.row = i;
          td.dataset.col = j;
          tr.appendChild(td);
        });
        table.appendChild(tr);
      });

      if (timer) clearInterval(timer);
      spustCasovac();
      pridatInterakci();
    } catch (error) {
      console.error("Chyba při načítání dat:", error);
    }
  };

  function spustCasovac() {
    const casElement = document.getElementById("cas");
    timer = setInterval(() => {
      casZbyva--;
      casElement.textContent = casZbyva;
      if (casZbyva <= 0) {
        clearInterval(timer);
        ukoncitHru();
      }
    }, 1000);
  }

  function pridatInterakci() {
    let oznacuje = false;
    let smer = null;

    table.removeEventListener("mousedown", handleMouseDown);
    table.removeEventListener("mousemove", handleMouseMove);
    table.removeEventListener("mouseup", handleMouseUp);
    table.removeEventListener("mouseleave", handleMouseLeave);

    table.addEventListener("mousedown", handleMouseDown);
    table.addEventListener("mousemove", handleMouseMove);
    table.addEventListener("mouseup", handleMouseUp);
    table.addEventListener("mouseleave", handleMouseLeave);

    function handleMouseDown(e) {
      if (e.target.tagName === "TD") {
        oznacuje = true;
        vybranaPole = [e.target];
        e.target.classList.add("selected");
        smer = null;
        e.preventDefault();
      }
    }

    function handleMouseMove(e) {
      if (
        oznacuje &&
        e.target.tagName === "TD" &&
        !vybranaPole.includes(e.target)
      ) {
        const prvni = vybranaPole[0];
        const aktualni = e.target;
        const r1 = parseInt(prvni.dataset.row);
        const c1 = parseInt(prvni.dataset.col);
        const r2 = parseInt(aktualni.dataset.row);
        const c2 = parseInt(aktualni.dataset.col);

        if (vybranaPole.length === 1) {
          smer = urcitSmer(r1, c1, r2, c2);
          if (smer) {
            vybranaPole.push(aktualni);
            aktualni.classList.add("selected");
          }
        } else if (smer) {
          const dr = r2 - r1;
          const dc = c2 - c1;
          if (jeVeSmeru(dr, dc, smer)) {
            vybranaPole.push(aktualni);
            aktualni.classList.add("selected");
          }
        }
      }
    }

    function handleMouseUp() {
      if (oznacuje) {
        oznacuje = false;
        zkontrolovatSlovo();
      }
    }

    function handleMouseLeave() {
      if (oznacuje) {
        oznacuje = false;
        zkontrolovatSlovo();
      }
    }
  }

  function urcitSmer(r1, c1, r2, c2) {
    const dr = r2 - r1;
    const dc = c2 - c1;
    const smerList = [
      [0, 1],
      [0, -1],
      [1, 0],
      [-1, 0],
      [1, 1],
      [-1, -1],
      [1, -1],
      [-1, 1],
    ];

    for (let [sr, sc] of smerList) {
      if (dr === sr && dc === sc) {
        return [sr, sc];
      }
    }
    return null;
  }

  function jeVeSmeru(dr, dc, smer) {
    const smerR = smer[0];
    const smerC = smer[1];
    if (smerR === 0) return dr === 0 && Math.sign(dc) === smerC;
    if (smerC === 0) return dc === 0 && Math.sign(dr) === smerR;
    return (
      Math.abs(dr) === Math.abs(dc) &&
      Math.sign(dr) === smerR &&
      Math.sign(dc) === smerC
    );
  }

  function zkontrolovatSlovo() {
    const vybraneSlovo = vybranaPole.map((td) => td.textContent).join("");
    const zpetneSlovo = vybranaPole
      .map((td) => td.textContent)
      .reverse()
      .join("");

    if (
      slovaKNajiti.includes(vybraneSlovo) &&
      !nalezenaSlova.includes(vybraneSlovo)
    ) {
      nalezenaSlova.push(vybraneSlovo);
      vybranaPole.forEach((td) => {
        td.classList.remove("selected");
        td.classList.add("found");
      });
    } else if (
      slovaKNajiti.includes(zpetneSlovo) &&
      !nalezenaSlova.includes(zpetneSlovo)
    ) {
      nalezenaSlova.push(zpetneSlovo);
      vybranaPole.forEach((td) => {
        td.classList.remove("selected");
        td.classList.add("found");
      });
    } else {
      vybranaPole.forEach((td) => td.classList.remove("selected"));
    }
    vybranaPole = [];
  }

  function ukoncitHru() {
    table.style.pointerEvents = "none";

    let body = 0;
    nalezenaSlova.forEach((slovo) => {
      body += slovo.length; // Počítání bodů podle délky slova
    });

    // Odhalíme nenalezená slova
    const nenalezenaSlova = slovaKNajiti.filter(
      (slovo) => !nalezenaSlova.includes(slovo)
    );
    console.log("Nalezená slova:", nalezenaSlova);
    console.log("Nenalezená slova:", nenalezenaSlova);
    console.log("Pozice slov:", poziceSlov);

    nenalezenaSlova.forEach((slovo) => {
      if (poziceSlov && poziceSlov[slovo]) {
        const pozice = poziceSlov[slovo];
        pozice.forEach(([radek, sloupec]) => {
          const td = table.querySelector(
            `td[data-row="${radek}"][data-col="${sloupec}"]`
          );
          if (td && !td.classList.contains("found")) {
            td.classList.add("missed");
          } else if (!td) {
            console.warn(
              `Buňka pro slovo ${slovo} na [${radek},${sloupec}] nenalezena.`
            );
          }
        });
      } else {
        console.error(`Pozice pro slovo ${slovo} neexistují v poziceSlov!`);
      }
    });

    const vysledek = document.getElementById("vysledek");
    if (body > 0 || nalezenaSlova.length > 0) {
      vysledek.innerHTML = `Hra skončila!<br>Našel jsi ${nalezenaSlova.length} z ${slovaKNajiti.length} slov.<br>Celkové body: ${body}`;
    } else {
      console.warn("Body nebo nalezená slova nebyly nastavena správně.");
      vysledek.innerHTML = `Hra skončila!<br>Našel jsi ${nalezenaSlova.length} z ${slovaKNajiti.length} slov.<br>Celkové body: 0`;
    }
  }
});
