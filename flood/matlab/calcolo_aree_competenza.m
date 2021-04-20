clear
close all


% % % % % dato il raster dei puntatori e un insieme di sezioni, suddivide il
% % % % % dominio idrologico in aree di competenza idraulica delle sezioni
% % % % 
% % % % 
% % % % inpath_DOMINI='./domini_idrologici/';       % directory dove si trovano i domini idrologici con i raster (nelle directory LandData), nodata=-9999
% % % % nome_dominio='ACP1';                        % nome del dominio idrologico (come compare nei file dei raster)
% % % % file_sezioni='sezioni_ACP1.txt';            % file di testo con le sezioni: le prime due colonne devono contenere le coordinate matrice i e j, la terza un identificativo intero

%% CARICO
%cd('C:\Users\Rocco\Desktop\CIMA Work\TESI\FILE M FLAVIO\AreeDrenate')
% carico puntatori
load('C:\Users\Rocco\Desktop\CIMA Work\TESI\FILE M FLAVIO\Data_LiguriaDomain.mat')
% nome dominio
nome_dominio='Graveglia';
% squadro
Lat_min=44.328;
Lat_max=44.350;
Lon_min=9.36;
Lon_max=9.44;




%% INDIVIDUO DOMINIO
% trovo indici 
temp=find(Londem(1,:)-Lon_min>0);
indice_y_min=temp(1);clear temp
temp=find(Londem(1,:)-Lon_max>0);
indice_y_max=temp(1);clear temp
temp=find(Latdem(:,1)-Lat_min>0);
indice_x_max=temp(end);clear temp
temp=find(Latdem(:,1)-Lat_max>0);
indice_x_min=temp(end);clear temp
% ritaglio mappe
Area_dominio=a2dArea(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Choice_dominio=a2iChoice(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Punt_dominio=a2iPunt(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Lat_dominio=Latdem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Lon_dominio=Londem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% coord UTM32
coord_top=4910830;
coord_bottom=4908400;
coord_right=528695;
coord_left=535079;
% [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_right:220:coord_left,coord_top:-220:coord_bottom);
[Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_right:220:coord_left,coord_bottom:220:coord_top);


%% SEZIONI
% sezione1
nome_sezione1='CAMINATA';
lat_sez1=44.34;
lon_sez1=9.41;
temp=find(Londem(1,:)-lon_sez1>0);
indice_y_sez1=temp(1);clear temp
temp=find(Latdem(:,1)-lat_sez1>0);
indice_x_sez1=temp(end);clear temp
sezioni(1,:)=[indice_x_sez1-indice_x_min+1,indice_y_sez1-indice_y_min+1];
codici_sezioni(1)=1;

nome_sezione1='GRAVEGLIA_OUT';
lat_sez2=44.3461;
lon_sez2=9.3623;
temp=find(Londem(1,:)-lon_sez2>0);
indice_y_sez2=temp(1);clear temp
temp=find(Latdem(:,1)-lat_sez2>0);
indice_x_sez2=temp(end);clear temp
sezioni(2,:)=[indice_x_sez2-indice_x_min+1,indice_y_sez2-indice_y_min+1];
codici_sezioni(2)=2;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% metto a posto i numeri che se no sono sbagliati
sezioni=[7,18;4,3];


%% AREE DRENATE
% calcolo aree a monte deele sezioni
aree=aree_drenate(Punt_dominio,sezioni);                                                                         % cell array con gli indici matrice di tutte le celle a monte di una data sezione

% Eliminazione aree drenate sovrapposte
mappa_aree=zeros(size(Punt_dominio));
L=cellfun(@length,aree);
[ordinati,indici_sort]=sort(L);
for i=length(L):-1:1
    valori=unique(mappa_aree(indici_sort(i)));
    mappa_aree(aree{indici_sort(i)})=codici_sezioni(indici_sort(i));
end
% % % mappa_aree(mappa_aree==0)=NaN;                                                                          % mappa del dominio idrologico suddivisa in aree di competenza (ogni area ha come valore l'identificativo della sezione)
% % % Riempimento aree mancanti
% % % indici_mancanti=find(isnan(mappa_aree));
% % % indici_ok=find(isfinite(mappa_aree));
% % % xx=1:size(mappa_aree,2);
% % % yy=1:size(mappa_aree,1);
% % % [X,Y]=meshgrid(xx,yy);
% % % tic
% % % mappa_aree(indici_mancanti)=griddata(X(indici_ok),Y(indici_ok),mappa_aree(indici_ok),X(indici_mancanti),Y(indici_mancanti),'nearest');
% % % toc
% % % mappa_aree=mappa_aree.*double(Punt_dominio>-9000);


%% RIGRIGLIO
inpath_hazmaps='C:\Users\Flavio\Desktop\CIMA WORLD\PROGETTI\POR Liguria\FIUMI\Entella\BK\FINALI\'; % directory delle hazard maps di partenza, in formato geotiff
hm_max=1500;                        % valore massimo ammesso nelle hazard maps
nome_hazmaps='WD_max_q';% nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
nome_hazmaps1='_clipped.tif';

[A, R]=geotiffread([inpath_hazmaps,'q',num2str(500),'\',nome_hazmaps,num2str(500),nome_hazmaps1]);
[new_x,new_y]=meshgrid(R.XWorldLimits(1):R.CellExtentInWorldX:R.XWorldLimits(2)-R.CellExtentInWorldX,...
                       R.YWorldLimits(1):R.CellExtentInWorldY:R.YWorldLimits(2)-R.CellExtentInWorldY);
mappa_aree_new=griddata(Lat_dominio_UTM32,Lon_dominio_UTM32,mappa_aree,new_y,new_x,'nearest');

%% salvataggio
save(['aree_competenza_',nome_dominio]);                 % mappa delle aree competenza SULLA GRIGLIA IDROLOGICA (va rigrigliata con nearest sulla griglia idraulica)








%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% LORENZO
% caricamento dati
pnt=rasterasc2mat([inpath_DOMINI,nome_dominio,'/LandData/',nome_dominio,'.pnt.txt']);                   % lettura raster puntatori
[ret,x_dem,y_dem]=rasterasc2mat([inpath_DOMINI,nome_dominio,'/LandData/',nome_dominio,'.choice.txt']);  % lettura raster reticolo
[X_dem,Y_dem]=meshgrid(x_dem,y_dem);
if Y_dem(end,1)>Y_dem(1,1)
    Y_dem=flipud(Y_dem);
end
sezioni=load(file_sezioni);                                                                             % lettura sezioni
codici_sezioni=sezioni(:,3);                                                                           % identificativo sezioni

% calcolo aree a monte deele sezioni
aree=aree_drenate(pnt,sezioni);                                                                         % cell array con gli indici matrice di tutte le celle a monte di una data sezione

% Eliminazione aree drenate sovrapposte
mappa_aree=zeros(size(pnt));
L=cellfun(@length,aree);
[ordinati,indici_sort]=sort(L);
for i=length(L):-1:1
    valori=unique(mappa_aree(indici_sort(i)));
    mappa_aree(aree{indici_sort(i)})=codici_sezioni(indici_sort(i));
end
mappa_aree(mappa_aree==0)=NaN;                                                                          % mappa del dominio idrologico suddivisa in aree di competenza (ogni area ha come valore l'identificativo della sezione)

% Riempimento aree mancanti
indici_mancanti=find(isnan(mappa_aree));
indici_ok=find(isfinite(mappa_aree));
xx=1:size(mappa_aree,2);
yy=1:size(mappa_aree,1);
[X,Y]=meshgrid(xx,yy);
tic
mappa_aree(indici_mancanti)=griddata(X(indici_ok),Y(indici_ok),mappa_aree(indici_ok),X(indici_mancanti),Y(indici_mancanti),'nearest');
toc
mappa_aree=mappa_aree.*double(pnt>-9000);

% salvataggio
save(['aree_competenza_',nome_dominio],'mappa_aree','indici_sezioni','codici_sezioni');                 % mappa delle aree competenza SULLA GRIGLIA IDROLOGICA (va rigrigliata con nearest sulla griglia idraulica)




