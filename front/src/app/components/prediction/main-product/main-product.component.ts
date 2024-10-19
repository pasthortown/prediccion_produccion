import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';

@Component({
  selector: 'app-main-product',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './main-product.component.html',
  styleUrls: ['./main-product.component.scss']
})
export class MainProductComponent implements OnChanges {
  @Input('tiempo') tiempo: Date = new Date();
  @Input('prediccion') prediccion: any = null;
  retencion_time = 0;
  preparando_time = 0;

  ngOnChanges() {
    this.updateTimes();
  }

  updateTimes() {
    const minutos = this.tiempo.getMinutes();
    const segundos = this.tiempo.getSeconds();
    const inicioIntervalo = Math.floor(minutos / 10) * 10;
    const intervalo = minutos - inicioIntervalo;
    const fraccionSegundos = segundos / 60;
    if (intervalo >= 0 && intervalo <= 3) {
      const tiempoTotal = intervalo + fraccionSegundos;
      this.preparando_time = (tiempoTotal / 3) * 100;
      this.retencion_time = 0;
    }
    else if (intervalo > 3 && intervalo <= 9) {
      const tiempoTotal = (intervalo - 3) + fraccionSegundos;
      this.preparando_time = 100;
      this.retencion_time = (tiempoTotal / 6) * 100;
    }
  }
}
