async function buscarCliente() {
    const cpf = document.getElementById("cpf").value.trim();

    if (cpf.length < 3) {
      document.getElementById("resultadoCliente").textContent = "";  // limpa se pouco texto
      return;
    }

    try {
      const resp = await fetch(`/buscar_cliente?cpf=${encodeURIComponent(cpf)}`);
      const data = await resp.json();

      if (resp.ok) {
        document.getElementById("resultadoCliente").textContent =
          `Nome: ${data.nome} | Telefone: ${data.telefone}`;
      } else {
        document.getElementById("resultadoCliente").textContent = "Cliente não encontrado";
      }
    } catch {
      document.getElementById("resultadoCliente").textContent = "Erro ao buscar cliente";
    }
  }