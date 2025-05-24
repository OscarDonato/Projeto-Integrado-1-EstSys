  window.addEventListener("DOMContentLoaded", () => {
    const alertBox = document.getElementById("alert-box");
    if (alertBox && alertBox.textContent.trim() !== "") {
      alertBox.classList.add("show");
    }
  });

  /////////////////////////////    VENDAS        /////////////////////////

  async function buscarCliente() {
    const cpf = document.getElementById("cpf").value.trim();

    if (cpf.length < 3) {
      document.getElementById("resultadoCliente").textContent = "";  // limpa se pouco texto
      document.querySelector("input[name='cli_nome']").value = "";
      document.querySelector("input[name='cli_doc']").value = "";
      return;
    }

    try {
      const resp = await fetch(`/buscar_cliente?cpf=${encodeURIComponent(cpf)}`);
      const data = await resp.json();

      if (resp.ok) {
        document.querySelector("input[name='cli_nome']").value = data.nome;
        document.querySelector("input[name='cli_doc']").value = data.doc;
        document.getElementById("resultadoCliente").textContent =
          `Nome: ${data.nome} | Telefone: ${data.telefone}`;
      } else {
        document.querySelector("input[name='cli_nome']").value = '';
        document.querySelector("input[name='cli_doc']").value = '';
        document.getElementById("resultadoCliente").textContent = "Cliente não encontrado";
      }
    } catch {
      document.getElementById("resultadoCliente").textContent = "Erro ao buscar cliente";
    }
  }

  ///////////////////////////  CARRINHO   /////////////////////////////////////
  ////////////////// Mostra | esconde a sidebar e overlay ////////////////////

document.getElementById('toggleSidebarBtn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('overlay').classList.toggle('show');
  });

document.getElementById('lupa').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('overlay').classList.toggle('show');
  });

  document.querySelector('.close-btn').addEventListener('click', function () {
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
  });

  document.getElementById('overlay').addEventListener('click', function() {
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
  })


//////////////// Busca de dados JS <--> flask <--> BD///////////////////

let carrinho = [];

function buscarItem() {
  const tipo = document.getElementById('tipoItem').value;
  const texto = document.getElementById('buscaTexto').value;

  fetch(`/buscar-item?tipo=${tipo}&texto=${encodeURIComponent(texto)}`)
    .then(response => response.json())
    .then(dados => preencherTabelaBusca(dados, tipo))
    .catch(error => console.error('Erro na busca:', error));
}

// Preencher tabela lateral de busca
function preencherTabelaBusca(itens, tipo) {
  const tbody = document.querySelector('.sidebar .display_table tbody');
  tbody.innerHTML = '';

  itens.forEach(item => {
    const row = document.createElement('tr');

    // Criar o HTML da linha, sem o botão ainda
    row.innerHTML = `
      <td>${item.id}</td>
      <td>${item.nome}</td>
      <td>${item.observa}</td>
      <td></td> <!-- célula para o botão -->
    `;

    // Criar o botão
    const btn = document.createElement('div');
    btn.innerHTML = `<form action="/add_item_cart" method="GET">
                        <input type="hidden" id="tipo" name="tipo" value="${tipo}">
                        <input type="hidden" id="id" name="id" value="${item.id}">
                        <input type="hidden" id="itemnome" name="itemnome" value="${item.nome}">
                        <input type="hidden" id="descricao" name="descricao" value="${item.observa}">
                        <input type="hidden" id="preco" name="preco" value="${item.preco}">
                        <button type= "submit" formmethod="GET" class="cart-add" formaction="/add_item_cart">
                          <i class="bi bi-cart-plus"></i>
                        </button>
                    </form>`;

    // Adicionar evento ao botão
    btn.addEventListener('click', function (event) {
      // event.preventDefault();  ==> seria para impedir recarregamento, mas não deu pra fazer funcionar direito
      const form = btn.querySelector('form');
      adicionarAoCarrinho(form);
    });

    // Colocar o botão na última célula da linha
    row.lastElementChild.appendChild(btn);

    tbody.appendChild(row);
  });
}

function adicionarAoCarrinho(form) {
  // CHAMADO PELA FUNÇAO CRIADA ACIMA EM BTN
  id       = form.getElementById('id').value;
  tipo     = form.getElementById('tipo').value;
  itemnome = form.getElementById('itemnome').value;
  descr    = form.getElementById('descricao').value;
  preco    = form.getElementById('preco').value;

  fetch(`/add_item_cart?id=${id}&tipo=${tipo}&itemnome=${itemnome}&descricao=${descr}&preco=${preco}`)
    .then(response => response.json())
    .catch(error => console.error('Erro na busca:', error));
}

async function getQts() {
  try {
    const response = await fetch('/get_qts');
    const cartItens = await response.json();

    const form = document.getElementById('finalizarVenda');

    cartItens.forEach(row => {
      const nome = row[1].replaceAll(' ', '_') + "_qt";
      const input = document.getElementById(nome);
      if (input) {
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = nome;
        hiddenInput.value = input.value;
        form.appendChild(hiddenInput);
      }
    });

    // Envia o formulário principal depois de capturar os dados
    form.submit();
  } catch (error) {
    console.error('Erro ao buscar itens do carrinho:', error);
  }
}