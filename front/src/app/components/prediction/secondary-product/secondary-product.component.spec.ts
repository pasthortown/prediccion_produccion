import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecondaryProductComponent } from './secondary-product.component';

describe('SecondaryProductComponent', () => {
  let component: SecondaryProductComponent;
  let fixture: ComponentFixture<SecondaryProductComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SecondaryProductComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SecondaryProductComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
