import { Component, Input, OnInit } from '@angular/core';
import { ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { Antigen, PatientList, Recipient } from '@app/model/Patient';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { PatientService } from '@app/services/patient/patient.service';
import { map, startWith } from 'rxjs/operators';
import { hlaFullTextSearch } from '@app/directives/validators/configForm.directive';
import { ENTER, SPACE } from '@angular/cdk/keycodes';

@Component({
  selector: 'app-patient-detail-recipient',
  templateUrl: './patient-detail-recipient.component.html',
  styleUrls: ['./patient-detail-recipient.component.scss']
})
export class PatientDetailRecipientComponent extends ListItemDetailAbstractComponent implements OnInit {

  @Input() patients?: PatientList;
  @Input() item?: Recipient;

  public success: boolean = false;

  public form: FormGroup = new FormGroup({
    antigens: new FormControl('')
  });

  public allAntigens: Antigen[] = [];
  public filteredAntigensCodes: Observable<Antigen[]>;

  public loading: boolean = false;

  public separatorKeysCodes: number[] = [ENTER, SPACE];

  constructor(private _patientService: PatientService) {
    super(_patientService);

    this.filteredAntigensCodes = this.form.controls.antigens.valueChanges.pipe(
      startWith(''),
      map((value: string | Antigen) => {
        return !value || typeof value === 'string' ? value : value.raw_code;
      }),
      map(code => code ? hlaFullTextSearch(this.availableAntigens, code) : this.availableAntigens.slice())
    );
  }

  ngOnInit(): void {
    this._initAntigensCodes();
  }

  get selectedAntigens(): Antigen[] {
    return this.item ? this.item.parameters.hla_typing.hla_types_list : [];
  }

  get availableAntigens(): Antigen[] {
    const selectedAntigensCodes = [...new Set(this.selectedAntigens.map(antigen => antigen.raw_code))];
    return this.allAntigens.filter(a => !selectedAntigensCodes.includes(a.raw_code));
  }

  public addAntigen(a: Antigen, control: HTMLInputElement): void {
    if (!this.item || !a) {
      return;
    }

    this.item.parameters.hla_typing.hla_types_list.push(a);

    // reset input
    this.form.controls.antigens.reset();
    control.value = '';
  }

  public addNewAntigen(code: string, control: HTMLInputElement): void {
    if (!this.item || !code) {
      return;
    }

    const formattedCode = code.trim().toUpperCase();
    this.item.parameters.hla_typing.hla_types_list.push({ raw_code: formattedCode });

    // reset input
    this.form.controls.antigens.reset();
    control.value = '';
  }

  public removeAntigen(antigen: Antigen): void {
    if (!this.item) {
      return;
    }

    const index = this.item.parameters.hla_typing.hla_types_list.indexOf(antigen);

    if (index >= 0) {
      this.item.parameters.hla_typing.hla_types_list.splice(index, 1);
    }
  }

  public setCheckBoxValue(key: string, value: boolean): void {
    if (this.item && this.item.recipient_requirements[key] !== undefined) {
      this.item.recipient_requirements[key] = value;
    }
  }

  public handleSave(): void {
    if (!this.item) {
      return;
    }

    this.loading = true;
    this.success = false;
    this._patientService.saveRecipient(this.item)
    .then(() => this.success = true)
    .finally(() => this.loading = false);
  }

  private _initAntigensCodes(): void {
    if (!this.patients?.recipients) {
      return;
    }

    const allAntigens = [];
    for (const r of this.patients.recipients) {

      allAntigens.push(...r.parameters.hla_typing.hla_types_list);
    }

    this.allAntigens = [...new Set(allAntigens.map(a => a.raw_code))].map(code => {
      return { raw_code: code };
    }); // only unique
  }
}