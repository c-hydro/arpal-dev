clear


% Dato un set di hazard maps di partenza con assegnati tempi di ritorno,
% interpola altre hazard maps con tempo di ritorno qualsiasi (inferiore al massimo disponibile)



% PARAMETRI
nome_dominio='ACP1';                % nome dominio idrologico (come compare nei raster)
inpath_hazmaps=['./',nome_dominio,'/HAZARD_MAPS/']; % directory delle hazard maps di partenza, in formato geotiff
hm_max=1500;                        % valore massimo ammesso nelle hazard maps
nome_hazmaps='Hazmap_';             % nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
outpath=['./',nome_dominio,'/MAPPE_TR/'];           % directory dove verranno salvate le mappe di hazard interpolate
nome_hazmaps_out='Hazmap__';        % nome delle hazard maps interpolate
TR=[25 50 100 200 500 1000];        % tempi di ritorno per i quali sono disponibili le hazard maps di partenza
TR_interp=1:1000;                   % tempi di ritorno per i quali si vogliono le mappe di hazard interpolate





% caricamento hazard maps, ordinamento, preparazione e calcolo statistiche
for t=1:length(TR)
   mappa=geotiffread([inpath_hazmaps,nome_hazmaps,sprintf('%04.0f',TR(t)),'.tif']);
   mappa(mappa>10000)=NaN;                          % elimina eventuali nodata con valori alti
   if t==1
       [nrows,ncols]=size(mappa);
       HazMaps_3d=single(zeros(nrows,ncols,length(TR)+1));
   end
   HazMaps_3d(:,:,t+1)=min(hm_max,single(mappa));     % satura a hm_max
end
HazMaps_3d=sort(HazMaps_3d,3);                      % ORDINAMENTO MAPPE HAZARD

% mappe strettamente crescenti ovunque
nT=size(HazMaps_3d,3);
for t=2:nT
    mappa_sotto=squeeze(HazMaps_3d(:,:,t-1));
    mappa_sopra=squeeze(HazMaps_3d(:,:,t));
    indici=find((mappa_sopra-mappa_sotto)==0 & mappa_sotto>0);
    mappa_sopra(indici)=mappa_sopra(indici)+rand(length(indici),1);
    HazMaps_3d(:,:,t)=mappa_sopra;
end
clear mappa_sotto mappa_sopra;
HazMaps_3d=sort(HazMaps_3d,3);                      % ORDINAMENTO MAPPE HAZARD

% Calcolo aree e volumi delle mappe nominali
nT=size(HazMaps_3d,3);
[V,N]=deal(NaN(1,nT));
for t=1:nT
    mappa_h=squeeze(HazMaps_3d(:,:,t));
    V(t)=nansum(mappa_h(:));                       % calcolo volumi totali
    N(t)=nansum(mappa_h(:)>0);                     % calcolo aree inondate totali (numero di celle)
end
clear mappa_h;
V=V(2:end); N=N(2:end);

% Funzioni di area e volume
tttt=0:1000;
vvvv=pchip([0,TR],[0,V],tttt);
[unici,i1,i2]=unique(vvvv);
T=[0,TR];
V=[0,V];
N=[0,N];





% CALCOLO CURVA LIVELLI VIRTUALI - VOLUMI ------------------------%

tic

disp('');
disp('CALCOLO CURVA Livelli Virtuali - Volumi...');
h=waitbar(0);
tic
TR_add=TR_interp;
[livelli,volumi]=deal(zeros(length(TR_add),length(T)));
i1_old=0;
for t=1:length(TR_add)
    
    
    TT=TR_add(t);
    
    % Tempi di ritorno nominali di riferimento
    i2=find((TT-T)<0,1,'first');
    i1=i2-1;     % sbagliato per le nominali, quelle vengono ricopiate
    indice_nominale=find(ismember(TR,TT));
    if t==TR(end)
        i1=length(T)-1;
        i2=i1+1;
    end
    if isempty(indice_nominale)==0      % mappa nominale
        disp([num2str(TT),'  NOMINALE']);
        mappa_h_nominale=single(HazMaps_3d(:,:,indice_nominale+1));
    end
    
    
    % Estrazione mappe nominali inferiore (h1) e superiore (h2)
    if i1>i1_old
        h1=squeeze(HazMaps_3d(:,:,i1));
        h2=squeeze(HazMaps_3d(:,:,i2));
    end
    
    
    % VIRTUAL LAKE
    
    % Calcolo nucleo, corona, mappa_fattori e Virtual DEM
    if i1>i1_old
        if t==1
            [VDEM,mappa_fattori]=deal(single(zeros(size(h1))));
        else
            VDEM(:)=0;
            mappa_fattori(:)=0;
        end
        indici_battenti=find(h2);
        indici_nucleo=find(h1);
        indici_corona=setdiff(indici_battenti,indici_nucleo);
        valori_nucleo1=h1(indici_nucleo); if isempty(indici_nucleo), valori_nucleo1=0; end
        valori_nucleo2=h2(indici_nucleo);
        valori_corona2=h2(indici_corona);
        VDEM(indici_nucleo)=max(valori_nucleo1)-valori_nucleo1;
        VDEM(indici_corona)=max(valori_nucleo1)+(max(valori_corona2)-valori_corona2);
        LIVELLO2=max(VDEM(:));
        VH=LIVELLO2-VDEM;
        LIVELLO_MIN=max(valori_nucleo1);
        VH(VH<h1)=h1(VH<h1);  % per evitare che il livello idrico sia inferiore alla nominale inferiore
        mappa_fattori(indici_nucleo)=(VH(indici_nucleo)-valori_nucleo1)./(valori_nucleo2-valori_nucleo1);
        mappa_fattori(indici_corona)=1;
        if i1==1
            T1=0;
        else
            T1=TR(i1-1);
        end
        T2=TR(i2-1);
        passo=1/(T2-T1);
    end
    
    % Livello a passo regolare per costruire la curva livelli virtuali-volume
    LIVELLO=LIVELLO_MIN+(LIVELLO2-LIVELLO_MIN)*(t-T1)*passo;
    
    % Mappa interpolata
    if isempty(indice_nominale)==0      % mappa nominale
        mappa_h=single(mappa_h_nominale);
    else
        mappa_h=single(zeros(size(h1)));
        mappa_h(indici_battenti)=h1(indici_battenti)+max(0,(LIVELLO-(VDEM(indici_battenti)+h1(indici_battenti))))./mappa_fattori(indici_battenti);
    end
    
    % livelli virtuali-volumi
    indice_nominale_prima=find(ismember(TR,TT+1));
    if isempty(indice_nominale_prima)==0      % mappa prima di una nominale
        livelli(t+1,i1)=LIVELLO2;
        volumi(t+1,i1)=sum(sum(h2));
    end
    livelli(t,i1)=LIVELLO;
    volumi(t,i1)=sum(sum(mappa_h));
    
    i1_old=i1;
    
    waitbar(t/length(TR_add),h);
end
close(h);
% save(NOME_CURVA,'livelli','volumi');

toc
    





% CALCOLO MAPPE INTERPOLATE ----------------------------------%


% Calcolo mappe interpolate
disp('INTERPOLAZIONE...');
h=waitbar(0);
tic
i1_old=0;
for t=1:length(TR_add)
    
    TT=TR_add(t);
    nome_file_out=[outpath,'/',nome_hazmaps_out,'T',sprintf('%04.0f',TT),'.mat'];
    
    % Tempi di ritorno nominali di riferimento
    i2=find((TT-T)<0,1,'first');
    i1=i2-1;     % sbagliato per le nominali, quelle vengono ricopiate
    indice_nominale=find(ismember(TR,TT));
    if t==TR(end)
        i1=length(T)-1;
        i2=i1+1;
    end
    if isempty(indice_nominale)==0      % mappa nominale
        disp([num2str(TT),'  NOMINALE']);
        mappa_h_nominale=single(HazMaps_3d(:,:,indice_nominale+1));
    end
    
    
    % Interpolazione volume ed estrazione mappe nominali inferiore (h1) e superiore (h2)
    V_TT=interp1(tttt,vvvv,double(TT));
    if i1>i1_old
        h1=squeeze(HazMaps_3d(:,:,i1));
        h2=squeeze(HazMaps_3d(:,:,i2));
    end
    
    
    % VIRTUAL LAKE
    
      
    % Calcolo nucleo, corona, mappa_fattori e Virtual DEM
    if i1>i1_old
        if t==1
            [VDEM,mappa_fattori]=deal(single(zeros(size(h1))));
        else
            VDEM(:)=0;
            mappa_fattori(:)=0;
        end
        indici_battenti=find(h2);
        indici_nucleo=find(h1);
        indici_corona=setdiff(indici_battenti,indici_nucleo);
        valori_nucleo1=h1(indici_nucleo); if isempty(indici_nucleo), valori_nucleo1=0; end
        valori_nucleo2=h2(indici_nucleo);
        valori_corona2=h2(indici_corona);
        VDEM(indici_nucleo)=max(valori_nucleo1)-valori_nucleo1;
        VDEM(indici_corona)=max(valori_nucleo1)+(max(valori_corona2)-valori_corona2);
        LIVELLO2=max(VDEM(:));
        VH=LIVELLO2-VDEM;
        mappa_fattori(indici_nucleo)=(VH(indici_nucleo)-valori_nucleo1)./(valori_nucleo2-valori_nucleo1);
        mappa_fattori(indici_corona)=1;
        if i1==1
            T1=0;
        else
            T1=TR(i1-1);
        end
        T2=TR(i2-1);
    end
    
    
    % Mappa corrispondente al livello calcolato per ottenere un dato volume (per rispettare la curva tempi di ritorno-volumi)
    LIVELLO=interp1(volumi(T1+1:T2,i1),livelli(T1+1:T2,i1),V_TT);
    
    % Mappa interpolata
    if isempty(indice_nominale)==0      % mappa nominale
        mappa_h=single(mappa_h_nominale);
    else
        mappa_h=single(zeros(size(h1)));
        mappa_h(indici_battenti)=h1(indici_battenti)+max(0,(LIVELLO-(VDEM(indici_battenti)+h1(indici_battenti))))./mappa_fattori(indici_battenti);
    end
    
    i1_old=i1;
    
    
    % salvataggio mappa
    save(nome_file_out,'-v7.3','mappa_h');
    
    
    waitbar(t/length(TR_add),h);
    
end
toc
close(h);






























    