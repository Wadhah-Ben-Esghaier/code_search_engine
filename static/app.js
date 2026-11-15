const form = document.getElementById("search-form");
const input = document.getElementById("term");
const status = document.getElementById("status");
const resultsList = document.getElementById("results");
const articleSection = document.getElementById("article");
const submitButton = form.querySelector('button[type="submit"]');

const articleTitle = document.getElementById("article-title");
const articleText = document.getElementById("article-text");
const backButton = document.getElementById("back");

async function search(term) {
    const params = new URLSearchParams({ term: term, limit: "10" });
    const response = await fetch("/api/search?" + params);

    if (!response.ok) {
        throw new Error("La recherche a échoué.");
    }

    const data = await response.json();
    return data.results;
}


function renderResults(results) {
    resultsList.replaceChildren();

    for (const result of results) {
        const item = document.createElement("li");
        item.textContent = `${result.title} — score : ${result.score.toFixed(6)}`;
        resultsList.appendChild(item);
    }
}


form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const term = input.value.trim();

    if (!term) {
        status.textContent = "Saisis un mot à rechercher.";
        return;
    }

    submitButton.disabled = true;
    articleSection.hidden = true;
    resultsList.hidden = false;
    resultsList.replaceChildren();
    status.textContent = "Recherche en cours…";

    try {
        const results = await search(term);
        renderResults(results);
        status.textContent = results.length === 0 ? "Aucun résultat." : `${results.length} résultat(s).`;
    } catch (error) {
        status.textContent = "Impossible de récupérer les résultats. Vérifie que le serveur fonctionne.";
    } finally {
        submitButton.disabled = false;
    }
});
function renderResults(results) {
    resultsList.replaceChildren();

    for (const result of results) {
        const item = document.createElement("li");
        const button = document.createElement("button");
        const score = document.createElement("span");

        button.type = "button";
        button.textContent = result.title;
        button.addEventListener("click", () => openPage(result.id));

        score.textContent = ` — score : ${result.score.toFixed(6)}`;

        item.append(button, score);
        resultsList.appendChild(item);
    }
}
async function openPage(id) {
    status.textContent = "Chargement de l’article…";
    resultsList.hidden = true;
    articleSection.hidden = true;
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/pages/" + id);

        if (!response.ok) {
            throw new Error("Impossible de récupérer l’article.");
        }

        const page = await response.json();
        renderPage(page);
        status.textContent = "";
    } catch (error) {
        resultsList.hidden = false;
        status.textContent = "Impossible de charger l’article.";
    } finally {
        submitButton.disabled = false;
    }
}


function renderPage(page) {
    articleTitle.textContent = page.title;
    articleText.textContent = page.text;
    articleSection.hidden = false;
}


backButton.addEventListener("click", function () {
    articleSection.hidden = true;
    resultsList.hidden = false;
    status.textContent = "";
});