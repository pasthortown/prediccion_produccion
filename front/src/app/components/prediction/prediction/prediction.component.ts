import { Component, OnInit, OnDestroy } from '@angular/core';
import { MainProductComponent } from "../main-product/main-product.component";
import { SecondaryProductComponent } from "../secondary-product/secondary-product.component";
import { PredictionService } from '../../../services/prediction.service';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-prediction',
  standalone: true,
  providers: [PredictionService],
  imports: [HttpClientModule, MainProductComponent, SecondaryProductComponent],
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.scss']
})
export class PredictionComponent implements OnInit, OnDestroy {
  tiempo: Date = new Date();
  audio: HTMLAudioElement = new Audio();
  predicciones_dia: any = null;
  prediccion: any = null;
  intervalId: any;

  constructor(private predictionService: PredictionService) {
    this.audio = new Audio();
    this.audio.src = '/alert.mp3';  // Reemplaza con la ruta de tu archivo MP3
    this.audio.load();
  }

  playAudio(): void {
    this.audio.currentTime = 0;
    this.audio.play();
  }

  redondearAMultiploCanastas(canastas: number): number {
    return Math.round(canastas * 2) / 2;
  }

  canastasString(canastas: number): string {
    const canastasRedondeadas = this.redondearAMultiploCanastas(canastas);
    if (canastasRedondeadas % 1 === 0) {
      return `${canastasRedondeadas} Canasta${canastasRedondeadas > 1 ? 's' : ''}`;
    }
    if (canastasRedondeadas % 1 === 0.5) {
      const parteEntera = Math.floor(canastasRedondeadas);
      const textoParteEntera = parteEntera > 0 ? `${parteEntera} y ` : '';
      const textoPlural = parteEntera === 0 ? 'Canasta' : 'Canastas';
      return `${textoParteEntera}1/2 ${textoPlural}`;
    }
    return '0 Canastas';
  }

  redondearAMultiploFundas(canastas: number): string {
    const canastasRedondeadas = this.redondearAMultiploCanastas(canastas);
    const fundas = canastasRedondeadas / 3;
    const fundasCompletas = Math.floor(fundas);
    const fraccionFundas = fundas - fundasCompletas;
    let textoFraccion = '';
    if (fraccionFundas >= 1/6 - 0.01 && fraccionFundas < 1/3 - 0.01) {
      textoFraccion = '1/6';
    } else if (fraccionFundas >= 1/3 - 0.01 && fraccionFundas < 1/2 - 0.01) {
      textoFraccion = '1/3';
    } else if (fraccionFundas >= 1/2 - 0.01 && fraccionFundas < 2/3 - 0.01) {
      textoFraccion = '1/2';
    } else if (fraccionFundas >= 2/3 - 0.01 && fraccionFundas < 5/6 - 0.01) {
      textoFraccion = '2/3';
    } else if (fraccionFundas >= 5/6 - 0.01 && fraccionFundas < 1 - 0.01) {
      textoFraccion = '5/6';
    }
    let resultado = '';
    if (fundasCompletas > 0) {
      resultado += `${fundasCompletas}`;
    }
    if (textoFraccion) {
      if (resultado) {
        resultado += ` ${textoFraccion}`;
      } else {
        resultado = textoFraccion;
      }
    }
    if (!resultado) {
        return '0 Fundas';
    }
    return `${resultado} Funda${fundasCompletas + (textoFraccion ? 1 : 0) > 1 ? 's' : ''}`;
  }

  build_prediccion() {
    const ahora = new Date();
    const hora_actual = ahora.getHours().toString().padStart(2, '0');
    const minuto_actual = Math.floor(ahora.getMinutes() / 10) * 10;
    const minuto_actual_str = minuto_actual.toString().padStart(2, '0');
    const hora_minuto_actual = `${hora_actual}:${minuto_actual_str}`;
    let prediccion_intervalo_actual: any = null;
    this.predicciones_dia.predicciones.forEach((prediccion: any) => {
        if (prediccion.hora_desde === hora_minuto_actual) {
            prediccion_intervalo_actual = prediccion;
        }
    });
    let predicciones_producto: any[] = [];
    let peso_prediccion: number = 0;
    prediccion_intervalo_actual.prediccion.forEach((prediccion_producto: any) => {
      console.log(prediccion_producto);
      let peso_producto_prediccion = prediccion_producto.cuenta_prediccion > 0 ? prediccion_producto.cuenta_prediccion : 0
      let to_insert: any = {
        categoria: prediccion_producto.plu_target.toString().trim(),
        peso_producto_prediccion: peso_producto_prediccion,
        unidad: prediccion_producto.unidad.toString().trim(),
        prediccion: peso_producto_prediccion / prediccion_producto.peso_unitario
      };
      peso_prediccion += to_insert.peso_producto_prediccion;
      if (!prediccion_producto.plu_target.toString().trim().includes('RECARGADA')) {
        predicciones_producto.push(to_insert);
      }
    });
    let canastas = peso_prediccion * 1000 / 800;
    let fundas_str = this.redondearAMultiploFundas(canastas);
    canastas = this.redondearAMultiploCanastas(canastas);
    let canastas_str = this.canastasString(canastas);
    this.prediccion = {
      hora_desde: prediccion_intervalo_actual.hora_desde,
      hora_hasta: prediccion_intervalo_actual.hora_hasta,
      peso_prediccion: peso_prediccion,
      fundas: fundas_str,
      canastas: canastas_str,
      fecha_prediccion: ahora,
      predicciones_producto: predicciones_producto
    };
  }

  get_prediction() {
    const minutos = this.tiempo.getMinutes();
    const segundos = this.tiempo.getSeconds();
    if (minutos % 10 === 0 && segundos === 0) {
      this.playAudio();
      this.predictionService.get_prediction().then(r => {
        this.predicciones_dia = r;
        this.build_prediccion();
      }).catch(e => {
        this.predicciones_dia = null;
        console.log(e);
      });
    }
  }

  ngOnInit(): void {
    this.intervalId = setInterval(() => {
      this.tiempo = new Date();
      this.get_prediction();
    }, 1000);
    this.tiempo = new Date();
    this.predictionService.get_prediction().then(r => {
      this.predicciones_dia = r;
      this.build_prediccion();
    }).catch(e => {
      this.predicciones_dia = null;
      console.log(e);
    });
  }

  ngOnDestroy(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}
