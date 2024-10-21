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

  tiempo_preparacion_1 = '';
  tiempo_retencion_1 = '';
  tiempo_preparacion_2 = '';
  tiempo_retencion_2 = '';
  tiempo_preparacion_3 = '';
  tiempo_retencion_3 = '';
  tiempo_preparacion_4 = '';
  tiempo_retencion_4 = '';

  retencion_time_1 = 0;
  preparando_time_1 = 0;
  retencion_time_2 = 0;
  preparando_time_2 = 0;
  retencion_time_3 = 0;
  preparando_time_3 = 0;
  retencion_time_4 = 0;
  preparando_time_4 = 0;

  estado_1 = 'Preparada';
  estado_2 = 'Preparada';
  estado_3 = 'Preparada';
  estado_4 = 'Preparada';

  // Variables para controlar los intervalos de cada estado
  interval_1: any;
  interval_2: any;
  interval_3: any;
  interval_4: any;

  ngOnChanges() {}

  startRetencionPreparando(state: number) {
    const now = new Date();
    const tiempoPreparacion = this.formatTime(now); // Aplicar formato

    if (state === 1) {
      this.clearIntervals(1);
      this.estado_1 = 'Preparando';
      this.tiempo_preparacion_1 = tiempoPreparacion;
      const retencionTime = new Date(now.getTime() + 10 * 60000 + 30000); // Sumar 10 minutos y 30 segundos
      this.tiempo_retencion_1 = this.formatTime(retencionTime); // Aplicar formato
      this.startTimer(1);
    } else if (state === 2) {
      this.clearIntervals(2);
      this.estado_2 = 'Preparando';
      this.tiempo_preparacion_2 = tiempoPreparacion;
      const retencionTime = new Date(now.getTime() + 10 * 60000 + 30000);
      this.tiempo_retencion_2 = this.formatTime(retencionTime); // Aplicar formato
      this.startTimer(2);
    } else if (state === 3) {
      this.clearIntervals(3);
      this.estado_3 = 'Preparando';
      this.tiempo_preparacion_3 = tiempoPreparacion;
      const retencionTime = new Date(now.getTime() + 10 * 60000 + 30000);
      this.tiempo_retencion_3 = this.formatTime(retencionTime); // Aplicar formato
      this.startTimer(3);
    } else if (state === 4) {
      this.clearIntervals(4);
      this.estado_4 = 'Preparando';
      this.tiempo_preparacion_4 = tiempoPreparacion;
      const retencionTime = new Date(now.getTime() + 10 * 60000 + 30000);
      this.tiempo_retencion_4 = this.formatTime(retencionTime); // Aplicar formato
      this.startTimer(4);
    }
  }

  // Función para reiniciar el estado, los tiempos y mostrar el botón "Preparada"
  resetState(state: number) {
    if (state === 1) {
      this.clearIntervals(1);
      this.preparando_time_1 = 0;
      this.retencion_time_1 = 0;
      this.tiempo_preparacion_1 = '';
      this.tiempo_retencion_1 = '';
      this.estado_1 = 'Preparada';
    } else if (state === 2) {
      this.clearIntervals(2);
      this.preparando_time_2 = 0;
      this.retencion_time_2 = 0;
      this.tiempo_preparacion_2 = '';
      this.tiempo_retencion_2 = '';
      this.estado_2 = 'Preparada';
    } else if (state === 3) {
      this.clearIntervals(3);
      this.preparando_time_3 = 0;
      this.retencion_time_3 = 0;
      this.tiempo_preparacion_3 = '';
      this.tiempo_retencion_3 = '';
      this.estado_3 = 'Preparada';
    } else if (state === 4) {
      this.clearIntervals(4);
      this.preparando_time_4 = 0;
      this.retencion_time_4 = 0;
      this.tiempo_preparacion_4 = '';
      this.tiempo_retencion_4 = '';
      this.estado_4 = 'Preparada';
    }
  }

  startTimer(state: number) {
    let preparando_time = 0;
    let retencion_time = 0;
    let interval: any;

    if (state === 1) {
      interval = setInterval(() => {
        if (preparando_time <= 210) { // 3 minutos 30 segundos (210 segundos)
          this.preparando_time_1 = (preparando_time / 210) * 100;
          preparando_time += 1;
        } else if (preparando_time > 210 && retencion_time <= 420) { // 7 minutos (420 segundos)
          this.retencion_time_1 = (retencion_time / 420) * 100;
          retencion_time += 1;
        } else {
          clearInterval(this.interval_1);
        }
      }, 1000); // Cada segundo
      this.interval_1 = interval;
    }
    // Repetir para los otros estados (2, 3 y 4).
    if (state === 2) {
      interval = setInterval(() => {
        if (preparando_time <= 210) {
          this.preparando_time_2 = (preparando_time / 210) * 100;
          preparando_time += 1;
        } else if (preparando_time > 210 && retencion_time <= 420) {
          this.retencion_time_2 = (retencion_time / 420) * 100;
          retencion_time += 1;
        } else {
          clearInterval(this.interval_2);
        }
      }, 1000);
      this.interval_2 = interval;
    }
    if (state === 3) {
      interval = setInterval(() => {
        if (preparando_time <= 210) {
          this.preparando_time_3 = (preparando_time / 210) * 100;
          preparando_time += 1;
        } else if (preparando_time > 210 && retencion_time <= 420) {
          this.retencion_time_3 = (retencion_time / 420) * 100;
          retencion_time += 1;
        } else {
          clearInterval(this.interval_3);
        }
      }, 1000);
      this.interval_3 = interval;
    }
    if (state === 4) {
      interval = setInterval(() => {
        if (preparando_time <= 210) {
          this.preparando_time_4 = (preparando_time / 210) * 100;
          preparando_time += 1;
        } else if (preparando_time > 210 && retencion_time <= 420) {
          this.retencion_time_4 = (retencion_time / 420) * 100;
          retencion_time += 1;
        } else {
          clearInterval(this.interval_4);
        }
      }, 1000);
      this.interval_4 = interval;
    }
  }

  clearIntervals(state: number) {
    if (state === 1) clearInterval(this.interval_1);
    if (state === 2) clearInterval(this.interval_2);
    if (state === 3) clearInterval(this.interval_3);
    if (state === 4) clearInterval(this.interval_4);
  }

  formatTime(date: Date): string {
    const hours = this.padZero(date.getHours());
    const minutes = this.padZero(date.getMinutes());
    const seconds = this.padZero(date.getSeconds());
    return `${hours}:${minutes}:${seconds}`;
  }

  padZero(value: number): string {
    return value < 10 ? `0${value}` : `${value}`;
  }
}
