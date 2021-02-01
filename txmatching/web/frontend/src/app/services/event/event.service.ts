import { Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { first, map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { LoggerService } from '@app/services/logger/logger.service';
import { TxmEvent, TxmEvents } from '@app/model/Event';
import { TxmEventsGenerated } from '@app/generated';
import { parseTxmEvent, parseTxmEvents } from '@app/parsers/event.parsers';
import { AuthService } from '@app/services/auth/auth.service';
import { Subscription } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EventService {

  _txmEvents?: Promise<TxmEvents>;
  _defaultTxmEvent?: Promise<TxmEvent>;
  _userSubscription: Subscription;

  constructor(private _http: HttpClient,
              private _logger: LoggerService,
              private _authService: AuthService) {
    // Remove cached events when user changes
    this._userSubscription = this._authService.currentUser.subscribe(_ => {
      this._txmEvents = undefined;
      this._defaultTxmEvent = undefined;
    })
  }

  public async getEvents(): Promise<TxmEvents> {
    if(!this._txmEvents) {
      this._txmEvents = this._http.get<TxmEventsGenerated>(
        `${environment.apiUrl}/txm-event`
      ).pipe(
        first(),
        map(parseTxmEvents)
      ).toPromise();
    }
    return this._txmEvents;
  }

  public getDefaultEvent(): Promise<TxmEvent> {
    if(!this._defaultTxmEvent) {
      this._defaultTxmEvent = this._http.get<TxmEvent>(
        `${environment.apiUrl}/txm-event/default`
      ).pipe(
        first(),
        map(parseTxmEvent)
      ).toPromise();
    }
    return this._defaultTxmEvent;
  }

  public setDefaultEvent(event_id: number): Promise<TxmEvent> {
    this._defaultTxmEvent = this._http.put<TxmEvent>(
      `${environment.apiUrl}/txm-event/default`,
      {
        id: event_id
      }
    ).pipe(
      first(),
      map(parseTxmEvent)
    ).toPromise();

    return this._defaultTxmEvent;
  }
}
