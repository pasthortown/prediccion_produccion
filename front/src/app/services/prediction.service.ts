import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class PredictionService {
  ws: string = 'http://localhost:5055/prediccion';

  options = {};

  constructor(private http: HttpClient) {
    let headers: HttpHeaders = new HttpHeaders().set('Content-Type', 'application/json');
    this.options = {headers: headers};
  }

  get_prediction(): Promise<any> {
    const fecha = new Date();
    const year = fecha.getFullYear();
    const month = ('0' + (fecha.getMonth() + 1)).slice(-2);
    const day = ('0' + (fecha.getDate())).slice(-2);
    const fechaStr = `/${year}/${month}/${day}`;

    return this.http.get(this.ws + fechaStr, this.options).toPromise();
  }

}
