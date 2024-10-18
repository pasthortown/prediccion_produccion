import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PredictionComponent } from "./components/prediction/prediction/prediction.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, PredictionComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'front';
}
