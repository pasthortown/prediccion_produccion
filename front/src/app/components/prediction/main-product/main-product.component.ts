import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-main-product',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './main-product.component.html',
  styleUrl: './main-product.component.scss'
})
export class MainProductComponent {
  @Input('tiempo') tiempo: Date = new Date();
  @Input('prediccion') prediccion: any = null;
}
