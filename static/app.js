const form = document.getElementById("company-search-form");
const innInput = document.getElementById("inn");
const resultSection = document.getElementById("company-result");
const errorSection = document.getElementById("error-message");
const errorText = errorSection.querySelector("p");

const companyStatus = document.getElementById("company-status");
const companyName = document.getElementById("company-name");
const companyInn = document.getElementById("company-inn");
const companyOgrn = document.getElementById("company-ogrn");
const companyKpp = document.getElementById("company-kpp");
const registrationDate = document.getElementById("company-registration-date");
const managerName = document.getElementById("company-manager");
const managerPosition = document.getElementById("company-manager-position");
const okvedCode = document.getElementById("company-okved-code");
const okvedName = document.getElementById("company-okved-name");
const companyAddress = document.getElementById("company-address");
const riskSummary = document.getElementById("risk-summary");
const riskList = document.getElementById("risk-list");


function showError(message) {
    resultSection.hidden = true;
    errorText.textContent = message;
    errorSection.hidden = false;
}


function formatDate(value) {
    if (!value) {
        return "—";
    }

    const [year, month, day] = value.split("-");

    if (!year || !month || !day) {
        return value;
    }

    return `${day}.${month}.${year}`;
}


function renderRiskChecks(riskChecks) {
    riskList.innerHTML = "";

    const entries = Object.entries(riskChecks || {});
    const hasRisks = entries.some(([, detected]) => detected);

    if (hasRisks) {
        riskSummary.textContent = "Обнаружены факторы, требующие внимания";
        riskSummary.classList.add("has-risk");
    } else {
        riskSummary.textContent = "Существенные факторы риска не обнаружены";
        riskSummary.classList.remove("has-risk");
    }

    for (const [label, detected] of entries) {
        const item = document.createElement("div");
        item.className = detected ? "risk-item risk-found" : "risk-item risk-clear";

        const indicator = document.createElement("span");
        indicator.className = "risk-indicator";
        indicator.textContent = detected ? "!" : "✓";

        const name = document.createElement("span");
        name.className = "risk-name";
        name.textContent = label;

        const status = document.createElement("strong");
        status.className = "risk-status";
        status.textContent = detected ? "Выявлено" : "Не выявлено";

        item.appendChild(indicator);
        item.appendChild(name);
        item.appendChild(status);

        riskList.appendChild(item);
    }
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorSection.hidden = true;
    resultSection.hidden = true;

    const inn = innInput.value.trim();

    if (!/^\d{10}$/.test(inn)) {
        showError("ИНН организации должен состоять из 10 цифр.");
        return;
    }

    const submitButton = form.querySelector("button");
    const originalButtonText = submitButton.textContent;

    submitButton.disabled = true;
    submitButton.textContent = "Проверяем";

    try {
        const response = await fetch(
            `/api/company?inn=${encodeURIComponent(inn)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Не удалось проверить организацию."
            );
        }

        companyStatus.textContent = data.status || "Статус не указан";
        companyName.textContent = data.name || "Название не указано";

        companyInn.textContent = data.inn || "—";
        companyOgrn.textContent = data.ogrn || "—";
        companyKpp.textContent = data.kpp || "—";

        registrationDate.textContent = formatDate(data.registration_date);

        managerName.textContent = data.manager?.name || "—";
        managerPosition.textContent = data.manager?.position || "—";

        okvedCode.textContent = data.okved?.code || "—";
        okvedName.textContent = data.okved?.name || "—";

        companyAddress.textContent = data.legal_address || "—";

        renderRiskChecks(data.risk_checks);

        resultSection.hidden = false;

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });

    } catch (error) {
        showError(
            error.message || "Произошла неизвестная ошибка."
        );

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});