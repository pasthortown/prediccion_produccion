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
    const intervalo = minutos % 10;
    if (intervalo <= 3) {
      this.preparando_time = (intervalo / 3) * 100;
      this.retencion_time = 0;
    } else {
      this.preparando_time = 100;
      this.retencion_time = ((intervalo - 3) / 7) * 100;
    }
  }
}
