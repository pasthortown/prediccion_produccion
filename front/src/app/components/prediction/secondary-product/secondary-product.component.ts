import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-secondary-product',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './secondary-product.component.html',
  styleUrl: './secondary-product.component.scss'
})
export class SecondaryProductComponent {

  @Input('prediccion_subproducto') prediccion_subproducto: any = null;
}
