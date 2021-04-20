clear

%% PARAMETRI
% nome_dominio='Graveglia';   % nome dominio idrologico (come compare nei raster)
% nome_dominio='Trebbia';   % nome dominio idrologico (come compare nei raster)
nome_dominio='Scrivia';   % nome dominio idrologico (come compare nei raster)


inpath_hazmaps=[pwd,'/telemac_map/',nome_dominio,'/']; % directory delle hazard maps di partenza, in formato geotiff
hm_max=1500;                        % valore massimo ammesso nelle hazard maps
% nome_hazmaps='WD_max_q';% nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
% nome_hazmaps1='_clipped.tif';
nome_hazmaps=[nome_dominio,'_','WD_max_Q'];% nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
nome_hazmaps1='.tif';
outpath=[pwd,'/hazmap/',nome_dominio,'/'];           % directory dove verranno salvate le mappe di hazard interpolate
nome_hazmaps_out=[nome_dominio,'_hazmap_'];        % nome delle hazard maps interpolate
TR=[5 10 20 25 30 40 50 70 100 150 200 500];        % tempi di ritorno per i quali sono disponibili le hazard maps di partenza
TR_interp=1:500;                   % tempi di ritorno per i quali si vogliono le mappe di hazard interpolate


%% LOAD
% caricamento hazard maps e calcolo statistiche
for t=1:length(TR)
mappa=geotiffread([inpath_hazmaps,nome_hazmaps,sprintf('%03.0f',TR(t)),nome_hazmaps1]);
mappa(mappa>1000)=NaN;                          % elimina eventuali nodata con valori alti
mappa=round(mappa.*1000);
% % % % % %    if t==1
% % % % % %        [nrows,ncols]=size(mappa);
% % % % % %        HazMaps_3d=single(NaN(nrows,ncols,length(TR)));
% % % % % %    end
% % % % % % %    HazMaps_3d(:,:,t)=min(hm_max,single(mappa));     % satura a hm_max
% % % % % %    HazMaps_3d(:,:,t)=single(mappa);     % satura a hm_max
% % %    V(t)=nansum(mappa(:));
% % %    N(t)=nansum(mappa(:)>0);
HazMaps_3d(:,:,t)=single(mappa);
end
% mappa=sort(HazMaps_3d,3);                      % ORDINAMENTO MAPPE HAZARD
mappa=HazMaps_3d;                      % ORDINAMENTO MAPPE HAZARD
clear HazMaps_3d
[V,N]=deal(NaN(1,length(TR)));
for t=1:length(TR)
mappa_hm=squeeze(mappa(:,:,t));
V(t)=nansum(mappa_hm(:));                       % calcolo volumi totali
N(t)=nansum(mappa_hm(:)>0);                     % calcolo aree inondate totali (numero di celle)
end


%% Interpolazione funzioni di area e volume
tttt=0:max(TR_interp);
vvvv=pchip([0,TR],[0,V],tttt);
[unici,i1,i2]=unique(vvvv);
vvvv2=vvvv(i1);
if V(1)==0
    nnnn=pchip(V,N,vvvv2);
else
    nnnn=pchip([0,V],[0,N],vvvv2);
end
T=[TR];       % tempi di ritorno delle hazard maps di partenza
V=[V];        % volumi delle hazard maps di partenza
N=[N];        % aree inondate delle hazard maps di partenza



%% CICLO SUI TEMPI DI RITORNO
for t=5:length(TR_interp)
    
    TT=TR_interp(t);
    
    nome_file_out=[outpath,nome_hazmaps_out,'T',sprintf('%03.0f',TT),'.mat'];
    if length(find((t-T)==0))>0
        clear mappa_sopra mappa_sotto
        %         mappa_sua=round(100*geotiffread([inpath_hazmaps,'/',nome_hazmaps,sprintf('%03.0f',(T(find((t-T)==0)))),nome_hazmaps1]));
        mappa_sua=mappa(:,:,find((t-T)==0));
        mappa_h=uint16(mappa_sua);
        % salvataggio mappa
        save(nome_file_out,'-v7.3','mappa_h');
        mappa_sotto=mappa_sua;
        clear mappa_sua mappa_h mappa_sopra
    else
        
        % Tempi di ritorno di riferimento (immediatamente inferiore e immediatamente superiore tra quelli delle hazard maps di partenza)
        i2=find((TT-T)<0,1,'first');
        i1=i2-1;
                
        % Interpolazione area e volume
        Tresiduo=TT;
        Vresiduo=interp1(tttt,vvvv,double(Tresiduo));
        Nresiduo=ceil(interp1(vvvv2,nnnn,Vresiduo));
        V_TT=Vresiduo;
        N_TT=Nresiduo;
        Npixel_da_elim=floor(N(i2)-N_TT);

        if (exist('mappa_sopra'))==0
%             mappa_sopra=geotiffread([inpath_hazmaps,'\',nome_hazmaps,sprintf('%03.0f',(T(i2))),nome_hazmaps1]);
            mappa_sopra=mappa(:,:,i2);
        end
        if (exist('mappa_sotto'))==0
%             mappa_sotto=geotiffread([inpath_hazmaps,'\',nome_hazmaps,sprintf('%03.0f',(T(i1))),nome_hazmaps1]);
        end
        % Calcolo mappa interpolata
        h1=squeeze(mappa_sotto);
        h2=squeeze(mappa_sopra);
        indici1_2=setdiff(find(h2),find(h1));
        valori1_2=h2(indici1_2);
        [val_sort,indici_sort]=sort(valori1_2);
        mappa_h_nominale=h2;
        mappa_h_nominale(indici1_2(indici_sort(1:Npixel_da_elim)))=0;
        V_mappa=nansum(mappa_h_nominale(:));
        mappa_h=uint16(round(single(mappa_h_nominale)*(V_TT/V_mappa)));
        
        % salvataggio mappa
        save(nome_file_out,'-v7.3','mappa_h');
        clear mappa_h
    end
    
end
















%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LORENZO

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





% caricamento hazard maps e calcolo statistiche
for t=1:length(TR)
   mappa=geotiffread([inpath_hazmaps,nome_hazmaps,sprintf('%04.0f',TR(t)),'.tif']);
   mappa(mappa>10000)=NaN;                          % elimina eventuali nodata con valori alti
   if t==1
       [nrows,ncols]=size(mappa);
       HazMaps_3d=single(NaN(nrows,ncols,length(TR)));
   end
   HazMaps_3d(:,:,t)=min(hm_max,single(mappa));     % satura a hm_max
end
HazMaps_3d=sort(HazMaps_3d,3);                      % ORDINAMENTO MAPPE HAZARD
[V,N]=deal(NaN(1,length(TR)));
for t=1:length(TR)
    mappa_hm=squeeze(HazMaps_3d(:,:,t));
    V(t)=nansum(mappa_hm(:));                       % calcolo volumi totali
    N(t)=nansum(mappa_hm(:)>0);                     % calcolo aree inondate totali (numero di celle)
end
toc


% Interpolazione funzioni di area e volume
tttt=0:max(TR_interp);
vvvv=pchip([0,TR],[0,V],tttt);
[unici,i1,i2]=unique(vvvv);
vvvv2=vvvv(i1);
if V(1)==0
    nnnn=pchip(V,N,vvvv2);
else
    nnnn=pchip([0,V],[0,N],vvvv2);
end
T=[0,TR];       % tempi di ritorno delle hazard maps di partenza
V=[0,V];        % volumi delle hazard maps di partenza
N=[0,N];        % aree inondate delle hazard maps di partenza



% CICLO SUI TEMPI DI RITORNO
for t=1:length(TR_interp)
    
    TT=TR_interp(t);
    
    nome_file_out=[outpath,'/',nome_hazmaps_out,'T',sprintf('%04.0f',TT),'.mat'];
    if exist(nome_file_out,'file')==0
        
        % Tempi di ritorno di riferimento (immediatamente inferiore e immediatamente superiore tra quelli delle hazard maps di partenza)
        i2=find((TT-T)<0,1,'first');
        i1=i2-1;
                
        % Interpolazione area e volume
        Tresiduo=TT;
        Vresiduo=interp1(tttt,vvvv,double(Tresiduo));
        Nresiduo=ceil(interp1(vvvv2,nnnn,Vresiduo));
        V_TT=Vresiduo;
        N_TT=Nresiduo;
        Npixel_da_elim=floor(N(i1)-N_TT);
        
        % Calcolo mappa interpolata
        h1=squeeze(HazMaps_3d(:,:,i1));
        h2=squeeze(HazMaps_3d(:,:,i2));
        indici1_2=setdiff(find(h2),find(h1));
        valori1_2=h2(indici1_2);
        [val_sort,indici_sort]=sort(valori1_2);
        mappa_h_nominale=h2;
        mappa_h_nominale(indici1_2(indici_sort(1:Npixel_da_elim)))=0;
        V_mappa=nansum(mappa_h_nominale(:));
        mappa_h=uint16(round(single(mappa_h_nominale)*(V_TT/V_mappa)));
        
        % salvataggio mappa
        save(nome_file_out,'-v7.3','mappa_h');
        
    end
    
end

    