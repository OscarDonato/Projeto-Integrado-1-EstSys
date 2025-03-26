import { Component } from '@angular/core';

@Component({
  selector: 'app-cadastro-cliente',
  templateUrl: './cadastro-cliente.component.html',
  styleUrls: ['./cadastro-cliente.component.css']
})
export class CadastroClienteComponent {
  cliente = {
    nome: '',
    email: '',
    telefone: ''
  };

  onSubmit(form: any) {
    if (form.valid) {
      console.log('Cadastro realizado com sucesso', this.cliente);
      // Aqui você pode enviar os dados para uma API ou serviço
    } else {
      console.log('Formulário inválido');
    }
  }
}
