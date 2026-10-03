const mobileMenuButton = document.querySelector(".mobile-menu-button");
const mobileMenu = document.querySelector("#mobile-menu");

if (mobileMenuButton && mobileMenu) {
  mobileMenuButton.addEventListener("click", () => {
    const open = mobileMenu.classList.toggle("open");
    mobileMenuButton.setAttribute("aria-expanded", String(open));
    mobileMenuButton.textContent = open ? "Close" : "Menu";
  });
}


/* PROJECT BUDGET CALCULATOR */

const budgetCalculator = {
  hours: document.querySelector("#budget-hours"),
  rate: document.querySelector("#budget-rate"),
  contingency: document.querySelector("#budget-contingency"),
  fixed: document.querySelector("#budget-fixed"),
  fee: document.querySelector("#budget-fee"),

  laborOutput: document.querySelector("#budget-labor"),
  contingencyOutput: document.querySelector("#budget-contingency-result"),
  fixedOutput: document.querySelector("#budget-fixed-result"),
  feeOutput: document.querySelector("#budget-fee-result"),
  totalOutput: document.querySelector("#budget-total")
};

if (
  budgetCalculator.hours &&
  budgetCalculator.rate &&
  budgetCalculator.contingency &&
  budgetCalculator.fixed &&
  budgetCalculator.fee
) {

  const readNumber = element => {
    const value = Number.parseFloat(element.value);

    if (!Number.isFinite(value) || value < 0) {
      return 0;
    }

    return value;
  };

  const formatMoney = value =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD"
    }).format(value);

  const updateBudgetCalculator = () => {

    const hours = readNumber(budgetCalculator.hours);
    const rate = readNumber(budgetCalculator.rate);
    const contingencyPercent = readNumber(budgetCalculator.contingency);
    const fixedCosts = readNumber(budgetCalculator.fixed);
    const feePercent = readNumber(budgetCalculator.fee);

    const labor = hours * rate;

    const contingency =
      labor * (contingencyPercent / 100);

    const subtotal =
      labor +
      contingency +
      fixedCosts;

    const fees =
      subtotal * (feePercent / 100);

    const total =
      subtotal +
      fees;

    budgetCalculator.laborOutput.textContent =
      formatMoney(labor);

    budgetCalculator.contingencyOutput.textContent =
      formatMoney(contingency);

    budgetCalculator.fixedOutput.textContent =
      formatMoney(fixedCosts);

    budgetCalculator.feeOutput.textContent =
      formatMoney(fees);

    budgetCalculator.totalOutput.textContent =
      formatMoney(total);
  };

  [
    budgetCalculator.hours,
    budgetCalculator.rate,
    budgetCalculator.contingency,
    budgetCalculator.fixed,
    budgetCalculator.fee
  ].forEach(input => {
    input.addEventListener("input", updateBudgetCalculator);
  });

  updateBudgetCalculator();
}
