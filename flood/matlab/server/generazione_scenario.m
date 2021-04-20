function mappa_flood=generazione_scenario(nome_dominio,sezioni,portate)
% funzione che genera uno scenario di portata in accordo con le portate previste su ogni sezione




% nome_dominio='Graveglia';
% nome_dominio='Sturla';
% nome_dominio='Lavagna';
% nome_dominio='Entella';
% nome_dominio='EntellaCompleto';
% nome_dominio='Trebbia';
% nome_dominio='BormidaMillesimo';
% nome_dominio='BormidaSpigno';
% nome_dominio='Scrivia';



%% UTILI
cd('C:\Users\Flavio\Desktop\CIMA WORLD\PROGETTI\POR Liguria\Flood_HM_realtime\Flood_HM_realtime')
path_codice=pwd;
path_dati_input=[pwd,'\telemac_map\']; 

path_mappe_input=[pwd,'\hazmap\'];
path_mappe_output=[pwd,'\hazmap\'];

nome_hazmaps=[nome_dominio,'_','WD_max_Q'];% nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
nome_hazmaps1='.tif';
Tsoglia=2;     % tempo di ritorno al di sotto (strettamente) del quale la mappa di hazard si annulla
TR_max=500;   % tempo di ritorno massimo (eventuali valori superiori vengono saturati a questo valore)
nome_floodmap_out='FloodMap';                        % nome della mappa risultato


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% AREE DI COMPETENZA
% Graveglia
if strcmp(nome_dominio,'Graveglia')
% %     Lat_min=44.3278;
% %     Lat_max=44.3496;
% %     Lon_min=9.3607;
% %     Lon_max=9.4415;
% %     coord_top=4910906;
% %     coord_bottom=4908599;
% %     coord_left=528758;
% %     coord_right=535193;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Sturla
elseif strcmp(nome_dominio,'Sturla')
% %     Lat_min=44.3496;
% %     Lat_max=44.4309;
% %     Lon_min=9.3358;
% %     Lon_max=9.4005;
% %     coord_top=4919701;
% %     coord_bottom=4910808;
% %     coord_left=526764;
% %     coord_right=531873;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Lavagna
elseif strcmp(nome_dominio,'Lavagna')
% %     Lat_min=44.3555;
% %     Lat_max=44.4004;
% %     Lon_min=9.2560;
% %     Lon_max=9.3446;
% %     coord_top=4916358;
% %     coord_bottom=4911440;
% %     coord_left=520194;
% %     coord_right=527448;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Entella
elseif strcmp(nome_dominio,'Entella')
% %     Lat_min=44.2997;
% %     Lat_max=44.3616;
% %     Lon_min=9.3083;
% %     Lon_max=9.3696;
% %     coord_top=4912068;
% %     coord_bottom=4905302;
% %     coord_left=524250;
% %     coord_right=529243;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EntellaCompleto
elseif strcmp(nome_dominio,'EntellaCompleto')
% %     Lat_min=44.2997;
% %     Lat_max=44.4330;
% %     Lon_min=9.2531;
% %     Lon_max=9.4421;
% %     coord_top=4919702;
% %     coord_bottom=4905300;
% %     coord_left=520193;
% %     coord_right=535194;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])

    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Trebbia
elseif strcmp(nome_dominio,'Trebbia')
% %     Lat_min=44.5181;
% %     Lat_max=44.6134;
% %     Lon_min=9.2365;
% %     Lon_max=9.3047;
% %     coord_top=4939716;
% %     coord_bottom=4929518;
% %     coord_left=518748;
% %     coord_right=524177;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
    
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BormidaMillesimo
elseif strcmp(nome_dominio,'BormidaMillesimo')
% %     Lat_min=44.3043;
% %     Lat_max=44.3997;
% %     Lon_min=8.1481;
% %     Lon_max=8.2179;
% %     coord_top=4916511;
% %     coord_bottom=4906362;
% %     coord_left=432157;
% %     coord_right=437658;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])

    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BormidaSpigno
elseif strcmp(nome_dominio,'BormidaSpigno')
% %     Lat_min=44.3412;
% %     Lat_max=44.5030;
% %     Lon_min=8.2679;
% %     Lon_max=8.3376;
% %     coord_top=4927431;
% %     coord_bottom=4910222;
% %     coord_left=441134;
% %     coord_right=446705;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Scrivia    
elseif strcmp(nome_dominio,'Scrivia')
% %     Lat_min=44.5070;
% %     Lat_max=44.6264;
% %     Lon_min=8.9292;
% %     Lon_max=9.0625;
% %     coord_top=4941265;
% %     coord_bottom=4928354;
% %     coord_left=494377;
% %     coord_right=505110;
% %     [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
% %     % trovo indici
% %     temp=find((Londem(1,:)-Lon_min)<0);
% %     indice_y_min=temp(end);clear temp
% %     temp=find((Londem(1,:)-Lon_max)<0);
% %     indice_y_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_min)>0);
% %     indice_x_max=temp(end);clear temp
% %     temp=find((Latdem(:,1)-Lat_max)>0);
% %     indice_x_min=temp(end);clear temp
% %     save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
% %           'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
% %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    % load  
    load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
  
end

%% DOMINIO
% % carico puntatori
% load('Data_LiguriaDomain.mat')
% % ritaglio mappe
% Area_dominio=a2dArea(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% Choice_dominio=a2iChoice(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% Punt_dominio=a2iPunt(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% Lat_dominio=Latdem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% Lon_dominio=Londem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
% Qindice_dominio=a2dQindice(indice_x_min:indice_x_max,indice_y_min:indice_y_max);

%% SEZIONI

% % quante_sez=input('Quante sezioni?')
% % figure
% % imagesc(Area_dominio)
% % caxis([2 20])
% % [pointclick_x,pointclick_y] = ginput(quante_sez);
% % close all
% % sezioni_indici_relativi=[round(pointclick_y),round(pointclick_x)];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if strcmp(nome_dominio,'Graveglia')
    quante_sez=2;
    sezioni_indici_relativi=[ 7 19;...  % CAMIN-Caminata
                              3  4];    % OUT
% Sturla
elseif strcmp(nome_dominio,'Sturla')
    quante_sez=2;
    sezioni_indici_relativi=[26 15;...  % VIGNO-Vignolo
                             38  5];    % OUT
% Lavagna
elseif strcmp(nome_dominio,'Lavagna')
    quante_sez=1;
    sezioni_indici_relativi=[22 33];    % San Martino (nuovo)
% Entella
elseif strcmp(nome_dominio,'Entella')
    quante_sez=3;
    sezioni_indici_relativi=[9 16;...   % CARAS-Carasco
                             11 20;...  % PANES-Panesi
                             28 10];    % OUT
% EntellaCompleto
elseif strcmp(nome_dominio,'EntellaCompleto')
    quante_sez=6;
    sezioni_indici_relativi=[38 34;...  % San Martino (nuovo) 
                             27 45;...  % VIGNO-Vignolo
                             48 58;...  % CAMIN-Caminata
                             44 36;...  % CARAS-Carasco
                             45 40;...  % PANES-Panesi
                             62 30];    % OUT
% Trebbia
elseif strcmp(nome_dominio,'Trebbia')
    quante_sez=2;
    sezioni_indici_relativi=[24 17;...  % Rovegno (nuovo)
                              5 24];    % OUT
% BormidaMillesimo
elseif strcmp(nome_dominio,'BormidaMillesimo')
    quante_sez=3;
    sezioni_indici_relativi=[45  8;...  % MURIA-Murialdo
                              7 23;...  % Cengio (nuovo)
                              2 16];    % OUT
% BormidaSpigno
elseif strcmp(nome_dominio,'BormidaSpigno')
    quante_sez=4;
    sezioni_indici_relativi=[71  9;...  % Carcare (nuovo) 
                             67 22;...  % Ferrania (nuovo)
                              9 16;...  % PCRIX-Piana Crixia
                              4 21];    % OUT
% Scrivia    
elseif strcmp(nome_dominio,'Scrivia')
    quante_sez=2;
    sezioni_indici_relativi=[57 45;...  % Montoggio (nuovo)
                              3 10];    % OUT
end



%% AREE DRENATE
% cd(path_codice)
% % calcolo aree a monte deele sezioni
% aree=aree_drenate(Punt_dominio,sezioni_indici_relativi);                                                                       
% % Eliminazione aree drenate sovrapposte
% mappa_aree=zeros(size(Punt_dominio));
% L=cellfun(@length,aree);
% [ordinati,indici_sort]=sort(L);
% for i=length(L):-1:1
%     valori=unique(mappa_aree(indici_sort(i)));
%     mappa_aree(aree{indici_sort(i)})=i;
% end
% 
% % figure
% % imagesc(mappa_aree)
% % hold on
% % [canalix,canaliy]=find(Choice_dominio==1);
% % for indicew=1:length(canalix)
% %     plot(canaliy(indicew),canalix(indicew),'.k','markersize',6)
% % end
% % for indicew=1:length(sezioni_indici_relativi)
% %     plot(sezioni_indici_relativi(indicew,2),sezioni_indici_relativi(indicew,1),'or','markersize',6)
% % end

%% RIGRIGLIO
% name_file_read=[path_dati_input,nome_dominio,'\',nome_hazmaps,'500',nome_hazmaps1];
% [A, R]=geotiffread(name_file_read);
% [new_x,new_y]=meshgrid(R.XWorldLimits(1):R.CellExtentInWorldX:R.XWorldLimits(2)-R.CellExtentInWorldX,...
%                        R.YWorldLimits(1):R.CellExtentInWorldY:R.YWorldLimits(2)-R.CellExtentInWorldY);
% mappa_aree_new=griddata(Lat_dominio_UTM32,Lon_dominio_UTM32,mappa_aree,new_y,new_x,'nearest');
% % geotiffwrite(['prova_area',nome_dominio,'.tif'],double(mappa_aree_new),R, 'CoordRefSysCode',['EPSG:','32632'])
% % %     save([path_mappe_output,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'new_x','new_y',...
% % %           'mappa_aree_new','R','mappa_aree','Lat_dominio_UTM32','Lon_dominio_UTM32')
% figure
% imagesc(mappa_aree_new)
    
% load  
load([path_mappe_output,nome_dominio,'\Aree_competenza_',nome_dominio])



%% CALCOLO SCENARI
% portate=[600,1200,1400];
portate=[400,450,170,1000,1250,1300];

for uuu=1:quante_sez
    TT(uuu)=round(exp(((Qindice_dominio(sezioni_indici_relativi(uuu,1),sezioni_indici_relativi(uuu,2)).*0.5239)+...
        portate(uuu))./(Qindice_dominio(sezioni_indici_relativi(uuu,1),sezioni_indici_relativi(uuu,2)).*1.0433)));
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% GENERAZIONE MAPPE
[nrows,ncols]=size(mappa_aree_new);                                                     % dimensioni della griglia idraulica
for i=1:quante_sez
    indici_aree{i}=find(mappa_aree_new==i);                             % cell array con gli indici matrice delle aree di competenza
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
    load([path_mappe_input,nome_dominio,'\',nome_dominio,'_Hazmap_T',sprintf('%03.0f',T),'.mat'],'mappa_h');
% % % %     geotiffwrite(['prova_',num2str(T),'_',nome_dominio,'.tif'],double(mappa_h)./100,R, 'CoordRefSysCode',['EPSG:','32632'])
%     for j=1:length(indici_T)
%         mappa_flood(indici_aree{indici_T(j)})=mappa_h((indici_aree{indici_T(j)}));
%     end
    mappa_flood(indici_aree{indici_T})=mappa_h((indici_aree{indici_T}));

    clear mappa_h
end
mappa_flood=double(mappa_flood)./1000;

figure
pcolor(new_x,new_y,flipud(mappa_flood))
shading flat
caxis([0 7])
hold on
colormap([1 1 1;...
          .8 1 1;...
          .6 .94 1;...
          .04 .96 .96;...
          .04 .67 .96;...
           0 .45 .74;...
           0 0 1])
for i=1:num_sezioni
    plot(sezioni{i,5},sezioni{i,4},'.k','markersize',10)
end

geotiffwrite(['prova',nome_dominio,'.tif'],mappa_flood,R, 'CoordRefSysCode',['EPSG:','32632'])




%%
save([outpath,nome_floodmap_out],'-v7.3','mappa_flood');






















%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PROVE
mappa_ricordo=zeros(5074,2741);
verifica=zeros(5074,2741);
for T=5:100
    load([path_mappe_input,nome_dominio,'\',nome_dominio,'_Hazmap_T',sprintf('%03.0f',T),'.mat'],'mappa_h');
    verifica=verifica+(mappa_h>=mappa_ricordo);
    mappa_ricordo=mappa_h;
    clear mappa_h
end
imagesc(verifica)







% % % % sezioni{1,1}='CAMINATA';
% % % % sezioni{1,2}=44.34;
% % % % sezioni{1,3}=9.41;
% % % % sezioni{1,4}=4909704;
% % % % sezioni{1,5}=532676;
% % % % 
% % % % sezioni{2,1}='CHIESANUOVA';
% % % % sezioni{2,2}=44.3441;
% % % % sezioni{2,3}=9.3985;
% % % % sezioni{2,4}=4910166;
% % % % sezioni{2,5}=531770;
% % % % 
% % % % sezioni{3,1}='NE';
% % % % sezioni{3,2}=44.3485;
% % % % sezioni{3,3}=9.3859;
% % % % sezioni{3,4}=4910650;
% % % % sezioni{3,5}=530763;
% % % % 
% % % % sezioni{4,1}='GRAVEGLIA_OUT';
% % % % sezioni{4,2}=44.3461;
% % % % sezioni{4,3}=9.3623;
% % % % sezioni{4,4}=4910407;
% % % % sezioni{4,5}=528810;
% % % % 
% % % % portate=[50,70,100,150];
% % % % TT=portate;
% % % % nome_dominio='Graveglia';
% % % 
% % % %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % % sezioni{1,1}='1';
% % % sezioni{1,2}=44.6075;
% % % sezioni{1,3}=9.2996;
% % % sezioni{1,4}=4939391;
% % % sezioni{1,5}=523770;
% % % 
% % % sezioni{2,1}='2';
% % % sezioni{2,2}=44.6036;
% % % sezioni{2,3}=9.2910;
% % % sezioni{2,4}=4938957;
% % % sezioni{2,5}=523095;
% % % 
% % % sezioni{3,1}='3';
% % % sezioni{3,2}=44.5867;
% % % sezioni{3,3}=9.2800;
% % % sezioni{3,4}=4937081;
% % % sezioni{3,5}=522228;
% % % 
% % % sezioni{4,1}='4';
% % % sezioni{4,2}=44.5541;
% % % sezioni{4,3}=9.2866;
% % % sezioni{4,4}=4933464;
% % % sezioni{4,5}=522764;
% % % 
% % % sezioni{5,1}='5';
% % % sezioni{5,2}=44.5441;
% % % sezioni{5,3}=9.2584;
% % % sezioni{5,4}=4932334;
% % % sezioni{5,5}=520530;
% % % 
% % % sezioni{6,1}='6';
% % % sezioni{6,2}=44.5246;
% % % sezioni{6,3}=9.2482;
% % % sezioni{6,4}=4930176;
% % % sezioni{6,5}=519726;
% % % 