let cart = [];

function addProduct() {
  const name = document.getElementById('productName').value.trim();
  const price = parseFloat(document.getElementById('productPrice').value);
  const quantity = parseInt(document.getElementById('productQuantity').value);

  if (!name || isNaN(price) || isNaN(quantity) || quantity <= 0) {
    alert('Preencha corretamente todos os campos do produto!');
    return;
  }

  const subtotal = price * quantity;
  cart.push({ name, price, quantity, subtotal });

  renderCart();
  clearInputs();
}

function renderCart() {
  const cartBody = document.getElementById('cartBody');
  cartBody.innerHTML = '';

  cart.forEach((item, index) => {
    cartBody.innerHTML += `
      <tr>
        <td>${item.name}</td>
        <td>R$ ${item.price.toFixed(2)}</td>
        <td>${item.quantity}</td>
        <td>R$ ${item.subtotal.toFixed(2)}</td>
        <td><button class="delete-btn" onclick="removeProduct(${index})">Remover</button></td>
      </tr>
    `;
  });

  updateTotal();
}

function updateTotal() {
  const total = cart.reduce((acc, item) => acc + item.subtotal, 0);
  document.getElementById('totalAmount').innerText = `Total: R$ ${total.toFixed(2)}`;
}

function clearInputs() {
  document.getElementById('productName').value = '';
  document.getElementById('productPrice').value = '';
  document.getElementById('productQuantity').value = '';
}

function removeProduct(index) {
  cart.splice(index, 1);
  renderCart();
}

function finalizeSale() {
  if (cart.length === 0) {
    alert('Carrinho vazio! Adicione produtos antes de finalizar a venda.');
    return;
  }
  
  alert('Venda finalizada com sucesso! Obrigado.');
  cart = [];
  renderCart();
}
