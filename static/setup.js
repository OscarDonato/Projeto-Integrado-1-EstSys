function showTab(tabId) {
  document.getElementById("products").style.display = "none";
  document.getElementById("clients").style.display = "none";
  document.getElementById("services").style.display = "none";
  document.getElementById(tabId).style.display = "flex";
}

// add product antiga:
//
// function addProduct() {
//     const name = document.getElementById('productName').value;
//     const priceInput = document.getElementById('productPrice').value;
//     const priceFloat = parseFloat(priceInput);

//     if (name && !isNaN(priceFloat)) {
//         const priceFormatted = priceFloat.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

//         const row = `<tr>
//             <td>${name}</td>
//             <td data-raw-price="${priceFloat}">${priceFormatted}</td>
//             <td>
//                 <button class='edit-btn' onclick='editRow(this)'>✏️</button>
//                 <button class='delete-btn' onclick='deleteRow(this)'>🗑️</button>
//             </td>
//         </tr>`;
//         document.getElementById('product-list').innerHTML += row;
//     }
// }

function addProduct(event) {
  event.preventDefault();  // <- ESSENCIAL para impedir o recarregamento

  //recebe o formulário como um elemento só a partir de "event"
  const form = event.target;
  const name = form.productName.value;
  const priceInput = form.productPrice.value;
  const priceFloat = parseFloat(priceInput);

  if (name && !isNaN(priceFloat)) {
    const formData = new FormData(form);

    fetch('/cad_prod', {  // manda o formulário para o flask
      method: 'POST',
      body: formData
    })

    //recebe de volta do flask
    .then(res => res.ok ? res.text() : res.text().then(t => { throw new Error(t); })) 
    .then(() => {
      const priceFormatted = priceFloat.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      });

      const row = `<tr>
        <td>${name}</td>
        <td>${priceFormatted}</td>
        <td>
          <button onclick="editRow(this)">✏️</button>
          <button onclick="deleteRow(this)">🗑️</button>
        </td>
      </tr>`;
      document.getElementById('product-list').innerHTML += row;

      form.reset(); // limpa os campos
    })
    .catch(err => alert("Erro: " + err.message));
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


//Função antiga addClient
// function addClient() {
//   const name = document.getElementById("clientName").value;
//   let cpf = document.getElementById("clientCPF").value.replace(/\D/g, "");
//   cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
//   let phone = document.getElementById("clientPhone").value.replace(/\D/g, "");
//   phone = phone.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
//   if (name && cpf && phone) {
//     const row = `<tr><td>${name}</td><td>${cpf}</td><td>${phone}</td>
//         <td>
//             <button class='edit-btn' onclick='editRow(this)'>✏️</button>
//             <button class='delete-btn' onclick='deleteRow(this)'>🗑️</button>
//         </td></tr>`;
//     document.getElementById("client-list").innerHTML += row;
//   }
// }

function addClient() {
  const name = document.getElementById("clientName").value;
  let cpf = document.getElementById("clientCPF").value.replace(/\D/g, ""); // Removendo todos os caracteres que não são números
  let phone = document.getElementById("clientPhone").value.replace(/\D/g, "");

  // Validação do CPF (Deve conter exatamente 11 digitos)
  if (cpf.length !== 11) {
      alert("ERRO!\n(CPF deve conter 11 números E seguir formato XXX.XXX.XXX-XX)");
      return;
  }
  
  // Validação do número (Deve conter 11 digitos, incluindo o código de área)
  if (phone.length !== 11) {
      alert("ERRO!\n(Número de telefone deve conter 11 números E seguir formato (XX) XXXXX-XXXX)");
      return;
  }

  // Formatando o CPF para: XXX.XXX.XXX-XX
  cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");

  // Formatando o Telefone para (XX) XXXXX-XXXX
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
