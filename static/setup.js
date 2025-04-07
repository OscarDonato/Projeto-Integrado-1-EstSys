function showTab(tabId) {
  document.getElementById("products").style.display = "none";
  document.getElementById("clients").style.display = "none";
  document.getElementById("services").style.display = "none";
  document.getElementById(tabId).style.display = "flex";
}

function addProduct() {
  const name = document.getElementById("productName").value;
  const price = parseFloat(
    document.getElementById("productPrice").value
  ).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  if (name && price) {
    const row = `<tr><td>${name}</td><td>${price}
            <button class='edit-btn' onclick='editRow(this)'>✏️</button>
            <button class='delete-btn' onclick='deleteRow(this)'>🗑️</button>
        </td></tr>`;
    document.getElementById("product-list").innerHTML += row;
  }
}

function addClient() {
  const name = document.getElementById("clientName").value;
  let cpf = document.getElementById("clientCPF").value.replace(/\D/g, "");
  cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  let phone = document.getElementById("clientPhone").value.replace(/\D/g, "");
  phone = phone.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
  if (name && cpf && phone) {
    const row = `<tr><td>${name}</td><td>${cpf}</td><td>${phone}</td>
        <td>
            <button class='edit-btn' onclick='editRow(this)'>✏️</button>
            <button class='delete-btn' onclick='deleteRow(this)'>🗑️</button>
        </td></tr>`;
    document.getElementById("client-list").innerHTML += row;
  }
}

function addService() {
  const name = document.getElementById("serviceName").value;
  const price = parseFloat(
    document.getElementById("servicePrice").value
  ).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  if (name && price) {
    const row = `<tr><td>${name}</td><td>${price}</td>
        <td>
            <button class='edit-btn' onclick='editRow(this)'>✏️</button>
            <button class='delete-btn' onclick='deleteRow(this)'>🗑️</button>
        </td></tr>`;
    document.getElementById("service-list").innerHTML += row;
  }
}

//FUNÇÕES DE EDIÇÃO E EXCLUSÃO

function editRow(button) {
  const row = button.parentElement.parentElement;
  const cells = row.querySelectorAll("td:not(:last-child)"); // Excluí o conteúdo anterior

  cells.forEach((cell) => {
    const input = document.createElement("input");
    input.type = "text";
    input.value = cell.innerText;
    cell.innerHTML = "";
    cell.appendChild(input);
  });

  button.innerText = "✅"; // Troca o botão para salvar
  button.onclick = function () {
    saveRow(this);
  };
}

function saveRow(button) {
  const row = button.parentElement.parentElement;
  const inputs = row.querySelectorAll("input");

  inputs.forEach((input) => {
    input.parentElement.innerText = input.value; // Substitui o imput por texto
  });

  button.innerText = "✏️"; // Faz o botão voltar a ser o lápis de edição
  button.onclick = function () {
    editRow(this);
  };
}

function deleteRow(button) {
  button.parentElement.parentElement.remove();
}
