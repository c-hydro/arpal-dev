function mappa_flood=generazione_flood(nome_dominio,TT)



% Dato il dominio (nella cui directory corrispondente devono essere
% presenti tutte le mappe di hazard interpolate) e di cui deve essere
% disponibile la mappa delle aree di competenza, e dati i tempi di ritorno
% verificatisi in un dato istante in tutte le sezioni, produce la
% corrispondente mappa di battenti sulla griglia idraulica.
%
% INPUT
%    nome_dominio = nome del dominio idrologico, così come compare nei nomi dei raster
%    TT = vettore ordinato dei tempi di ritorno corrispondenti alle portate
%         in un dato istante in tutte le sezioni di interesse (quelle di cui si hanno le aree di competenza)



% PARAMETRI
Tsoglia=2;     % tempo di ritorno al di sotto (strettamente) del quale la mappa di hazard si annulla
TR_max=500;   % tempo di ritorno massimo (eventuali valori superiori vengono saturati a questo valore)
inpath_mappe_TR=['C:\Users\Flavio\Desktop\CIMA WORLD\PROGETTI\POR Liguria\Flood_HM_realtime\Flood_HM_realtime'];          
outpath=['C:\Users\Flavio\Desktop\CIMA WORLD\PROGETTI\POR Liguria\Flood_HM_realtime\Flood_HM_realtime'];           % directory dove verranno salvate le mappe di hazard interpolate% percorso in cui verrà salvata la mappa risultato
nome_floodmap_out='FloodMap';                        % nome della mappa risultato



% lettura dati
load(['aree_competenza_idro_',nome_dominio],'mappa_aree_new','codici_sezioni');         % mappa delle aree competenza SULLA GRIGLIA IDRAULICA
[nrows,ncols]=size(mappa_aree_new);                                                     % dimensioni della griglia idraulica
indici_aree=cell(length(codici_sezioni),1);
for i=1:length(codici_sezioni)
    indici_aree{i}=find(mappa_aree_new==i);                             % cell array con gli indici matrice delle aree di competenza
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% costruzione scenario
mappa_flood=uint16(zeros(nrows,ncols));
TT=max(1,min(TR_max,TT));
T_unici=unique(TT);
for i=1:length(T_unici)
    T=T_unici(i);
    if T<Tsoglia
        continue
    end
    indici_T=find(TT==T);
    load([inpath_mappe_TR,'Hazmap__T',sprintf('%04.0f',T),'.mat'],'mappa_h');
    for j=1:length(indici_T)
        mappa_flood(indici_aree{indici_T(j)})=mappa_h((indici_aree{indici_T(j)}));
    end
end

save([outpath,nome_floodmap_out],'-v7.3','mappa_flood');




%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LORENZO

% Dato il dominio (nella cui directory corrispondente devono essere
% presenti tutte le mappe di hazard interpolate) e di cui deve essere
% disponibile la mappa delle aree di competenza, e dati i tempi di ritorno
% verificatisi in un dato istante in tutte le sezioni, produce la
% corrispondente mappa di battenti sulla griglia idraulica.
%
% INPUT
%    nome_dominio = nome del dominio idrologico, così come compare nei nomi dei raster
%    TT = vettore ordinato dei tempi di ritorno corrispondenti alle portate
%         in un dato istante in tutte le sezioni di interesse (quelle di cui si hanno le aree di competenza)



% PARAMETRI
Tsoglia=2;     % tempo di ritorno al di sotto (strettamente) del quale la mappa di hazard si annulla
TR_max=1000;   % tempo di ritorno massimo (eventuali valori superiori vengono saturati a questo valore)
inpath_mappe_TR=['./',nome_dominio,'/MAPPE_TR/'];
outpath=['./',nome_dominio,'/MAPPE_FLOOD/'];        % percorso in cui verrà salvata la mappa risultato
nome_floodmap_out='FloodMap';                        % nome della mappa risultato



% lettura dati
load(['aree_competenza_idro_',nome_dominio],'mappa_aree','codici_sezioni');         % mappa delle aree competenza SULLA GRIGLIA IDRAULICA
[nrows,ncols]=size(mappa_aree);                                                     % dimensioni della griglia idraulica
indici_aree=cell(length(codici_sezioni),1);
for i=1:length(codici_sezioni_paese)
    indici_aree{i}=find(mappa_aree==codici_sezioni(i));                             % cell array con gli indici matrice delle aree di competenza
end



% costruzione scenario
mappa_flood=uint16(zeros(nrows,ncols));
TT=max(1,min(TR_max,TT));
T_unici=unique(TT);
for i=1:length(T_unici)
    T=T_unici(i);
    if T<Tsoglia
        continue
    end
    indici_T=find(TT==T);
    load([inpath_mappe_TR,'Hazmap__T',sprintf('%04.0f',T),'.mat'],'mappa_h');
    for j=1:length(indici_T)
        mappa_flood(indici_aree{indici_T(j)})=mappa_h((indici_aree{indici_T(j)}));
    end
end

save([outpath,nome_floodmap_out],'-v7.3','mappa_flood');


    


