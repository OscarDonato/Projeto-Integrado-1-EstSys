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
      // event.preventDefault();
      const form = btn.querySelector('form');
      adicionarAoCarrinho(form);
    });

    // Colocar o botão na última célula da linha
    row.lastElementChild.appendChild(btn);

    tbody.appendChild(row);
  });
}

function adicionarAoCarrinho(form) {

  id       = form.getElementById('id').value;
  tipo     = form.getElementById('tipo').value;
  itemnome = form.getElementById('itemnome').value;
  descr    = form.getElementById('descricao').value;
  preco    = form.getElementById('preco').value;

  fetch(`/add_item_cart?id=${id}&tipo=${tipo}&itemnome=${itemnome}&descricao=${descr}&preco=${preco}`)
    .then(response => response.json())
    .catch(error => console.error('Erro na busca:', error));
}
