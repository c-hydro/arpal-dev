function GENERAZIONE_SCENARIO_FLOOD(nome_dominio,mode)
% funzione che genera uno scenario di portata in accordo con le portate previste su ogni sezione
% possibili domini su cui operare sono:
% nome_dominio='Graveglia';
% nome_dominio='Sturla';
% nome_dominio='Lavagna';
% nome_dominio='Entella';
% nome_dominio='EntellaCompleto';
% nome_dominio='Trebbia';
% nome_dominio='BormidaMillesimo';
% nome_dominio='BormidaSpigno';
% nome_dominio='Scrivia';
% modalità di utilizzo
% mode=1 %-->operativo
% mode=0 %-->preparazione
% esempio:
% GENERAZIONE_SCENARIO_FLOOD('EntellaCompleto',1)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% UTILI: variabili utili
% percorso dove si trova il codice
cd('C:\Users\Flavio\Desktop\CIMA WORLD\PROGETTI\POR Liguria\Flood_HM_realtime\Flood_HM_realtime')
path_codice=pwd;

% percorso dove si trovano le simulazioni
path_dati_input=[pwd,'\telemac_map\'];
% percorso dove si trovano gli scenari
path_mappe_input=[pwd,'\hazmap\'];
path_mappe_output=[pwd,'\hazmap\'];
% composizione nome file scenari
nome_hazmaps=[nome_dominio,'_','WD_max_Q'];% nome delle hazard maps di partenza (es:  [nome_hazmaps]0025.mat )
nome_hazmaps1='.tif';
% nome della mappa risultato
nome_floodmap_out='FloodMap';

% tempo di ritorno al di sotto (strettamente) del quale la mappa di hazard si annulla
Tsoglia=5;
% tempo di ritorno massimo (eventuali valori superiori vengono saturati a questo valore)
TR_max=500;

% carico dati modello idrogeologico
load('Data_LiguriaDomain.mat')


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% AREE DI COMPETENZA: definisco le aree di competenza di ciascuna sezione
% mode operativo
if mode==1
    % Graveglia
    if strcmp(nome_dominio,'Graveglia')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        
        % Sturla
    elseif strcmp(nome_dominio,'Sturla')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % Lavagna
    elseif strcmp(nome_dominio,'Lavagna')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % Entella
    elseif strcmp(nome_dominio,'Entella')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % EntellaCompleto
    elseif strcmp(nome_dominio,'EntellaCompleto')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % Trebbia
    elseif strcmp(nome_dominio,'Trebbia')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % BormidaMillesimo
    elseif strcmp(nome_dominio,'BormidaMillesimo')
        % %           'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % BormidaSpigno
    elseif strcmp(nome_dominio,'BormidaSpigno')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
        % Scrivia
    elseif strcmp(nome_dominio,'Scrivia')
        % load
        load([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio])
    end
    
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
% mode preparazione
else
    % Graveglia
    if strcmp(nome_dominio,'Graveglia')
        Lat_min=44.3278;
        Lat_max=44.3496;
        Lon_min=9.3607;
        Lon_max=9.4415;
        coord_top=4910906;
        coord_bottom=4908599;
        coord_left=528758;
        coord_right=535193;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Sturla
    elseif strcmp(nome_dominio,'Sturla')
        Lat_min=44.3496;
        Lat_max=44.4309;
        Lon_min=9.3358;
        Lon_max=9.4005;
        coord_top=4919701;
        coord_bottom=4910808;
        coord_left=526764;
        coord_right=531873;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Lavagna
    elseif strcmp(nome_dominio,'Lavagna')
        Lat_min=44.3555;
        Lat_max=44.4004;
        Lon_min=9.2560;
        Lon_max=9.3446;
        coord_top=4916358;
        coord_bottom=4911440;
        coord_left=520194;
        coord_right=527448;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Entella
    elseif strcmp(nome_dominio,'Entella')
        Lat_min=44.2997;
        Lat_max=44.3616;
        Lon_min=9.3083;
        Lon_max=9.3696;
        coord_top=4912068;
        coord_bottom=4905302;
        coord_left=524250;
        coord_right=529243;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % EntellaCompleto
    elseif strcmp(nome_dominio,'EntellaCompleto')
        Lat_min=44.2997;
        Lat_max=44.4330;
        Lon_min=9.2531;
        Lon_max=9.4421;
        coord_top=4919702;
        coord_bottom=4905300;
        coord_left=520193;
        coord_right=535194;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Trebbia
    elseif strcmp(nome_dominio,'Trebbia')
        Lat_min=44.5181;
        Lat_max=44.6134;
        Lon_min=9.2365;
        Lon_max=9.3047;
        coord_top=4939716;
        coord_bottom=4929518;
        coord_left=518748;
        coord_right=524177;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % BormidaMillesimo
    elseif strcmp(nome_dominio,'BormidaMillesimo')
        Lat_min=44.3043;
        Lat_max=44.3997;
        Lon_min=8.1481;
        Lon_max=8.2179;
        coord_top=4916511;
        coord_bottom=4906362;
        coord_left=432157;
        coord_right=437658;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % BormidaSpigno
    elseif strcmp(nome_dominio,'BormidaSpigno')
        Lat_min=44.3412;
        Lat_max=44.5030;
        Lon_min=8.2679;
        Lon_max=8.3376;
        coord_top=4927431;
        coord_bottom=4910222;
        coord_left=441134;
        coord_right=446705;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Scrivia
    elseif strcmp(nome_dominio,'Scrivia')
        Lat_min=44.5070;
        Lat_max=44.6264;
        Lon_min=8.9292;
        Lon_max=9.0625;
        coord_top=4941265;
        coord_bottom=4928354;
        coord_left=494377;
        coord_right=505110;
        [Lon_dominio_UTM32,Lat_dominio_UTM32]=meshgrid(coord_left:220:coord_right,coord_bottom:220:coord_top);
        % trovo indici
        temp=find((Londem(1,:)-Lon_min)<0);
        indice_y_min=temp(end);clear temp
        temp=find((Londem(1,:)-Lon_max)<0);
        indice_y_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_min)>0);
        indice_x_max=temp(end);clear temp
        temp=find((Latdem(:,1)-Lat_max)>0);
        indice_x_min=temp(end);clear temp
        save([path_dati_input,nome_dominio,'\Aree_competenza_',nome_dominio,'.mat'],'Lat_min','Lat_max',...
            'Lon_min','Lon_max','coord_top','coord_bottom','coord_left','coord_right','Lon_dominio_UTM32',...
            'Lat_dominio_UTM32','indice_y_min','indice_y_max','indice_x_max','indice_x_min')
    end
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% DOMINIO: definisco il dominio di lavoro
% ritaglio mappe
Area_dominio=a2dArea(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Choice_dominio=a2iChoice(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Punt_dominio=a2iPunt(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Lat_dominio=Latdem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Lon_dominio=Londem(indice_x_min:indice_x_max,indice_y_min:indice_y_max);
Qindice_dominio=a2dQindice(indice_x_min:indice_x_max,indice_y_min:indice_y_max);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% SEZIONI: definisco dove sono le sezioni di controllo
% mode operativo
if mode==1
    % Graveglia
    if strcmp(nome_dominio,'Graveglia')
        quante_sez=2;
        sezioni_indici_relativi=[ 7 19;...  % CAMIN-Caminata
                                  3  4];    % OUT
        nomi_sezioni{1}='CAMIN-Caminata';
        nomi_sezioni{2}='OUT';
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Sturla
    elseif strcmp(nome_dominio,'Sturla')
        quante_sez=2;
        sezioni_indici_relativi=[26 15;...  % VIGNO-Vignolo
                                 38  5];    % OUT
        nomi_sezioni{1}='VIGNO-Vignolo';
        nomi_sezioni{2}='OUT';
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Lavagna
    elseif strcmp(nome_dominio,'Lavagna')
        quante_sez=1;
        sezioni_indici_relativi=[22 33];    % San Martino (nuovo)
        nomi_sezioni{1}='San Martino';
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Entella
    elseif strcmp(nome_dominio,'Entella')
        quante_sez=3;
        sezioni_indici_relativi=[9 16;...   % CARAS-Carasco
                                11 20;...   % PANES-Panesi
                                28 10];     % OUT
        nomi_sezioni{1}='CARAS-Carasco';
        nomi_sezioni{2}='PANES-Panesi';
        nomi_sezioni{3}='OUT';
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % EntellaCompleto
    elseif strcmp(nome_dominio,'EntellaCompleto')
        quante_sez=6;
        sezioni_indici_relativi=[38 34;...  % San Martino (nuovo)
                                 27 45;...  % VIGNO-Vignolo
                                 48 58;...  % CAMIN-Caminata
                                 44 36;...  % CARAS-Carasco
                                 45 40;...  % PANES-Panesi
                                 62 30];    % OUT
        nomi_sezioni{1}='San Martino';
        nomi_sezioni{2}='VIGNO-Vignolo';
        nomi_sezioni{3}='CAMIN-Caminata';
        nomi_sezioni{4}='CARAS-Carasco';
        nomi_sezioni{5}='PANES-Panesi';
        nomi_sezioni{6}='OUT';

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Trebbia
    elseif strcmp(nome_dominio,'Trebbia')
        quante_sez=2;
        sezioni_indici_relativi=[24 17;...  % Rovegno (nuovo)
                                  5 24];    % OUT
        nomi_sezioni{1}='Rovegno';
        nomi_sezioni{2}='OUT';
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % BormidaMillesimo
    elseif strcmp(nome_dominio,'BormidaMillesimo')
        quante_sez=3;
        sezioni_indici_relativi=[45  8;...  % MURIA-Murialdo
                                  7 23;...  % Cengio (nuovo)
                                  2 16];    % OUT
        nomi_sezioni{1}='MURIA-Murialdo';
        nomi_sezioni{2}='Cengio';
        nomi_sezioni{3}='OUT';
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % BormidaSpigno
    elseif strcmp(nome_dominio,'BormidaSpigno')
        quante_sez=4;
        sezioni_indici_relativi=[71  9;...  % Carcare (nuovo)
                                 67 22;...  % Ferrania (nuovo)
                                  9 16;...  % PCRIX-Piana Crixia
                                  4 21];    % OUT
        nomi_sezioni{1}='Carcare';
        nomi_sezioni{2}='Ferrania';
        nomi_sezioni{3}='PCRIX-Piana Crixia';
        nomi_sezioni{4}='OUT';
        
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Scrivia
    elseif strcmp(nome_dominio,'Scrivia')
        quante_sez=2;
        sezioni_indici_relativi=[57 45;...  % Montoggio (nuovo)
                                  3 10];    % OUT
        nomi_sezioni{1}='Montoggio';
        nomi_sezioni{2}='OUT';
    end
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % mode preparazione
else
    % numero sezioni
    quante_sez=input('Quante sezioni?')
    figure
    imagesc(Area_dominio)
    caxis([2 20])
    % scelgo dove sono le sezioni
    [pointclick_x,pointclick_y] = ginput(quante_sez);
    close all
    % costruisco file delle sezioni
    sezioni_indici_relativi=[round(pointclick_y),round(pointclick_x)];
    % nomi sezioni
    for ind=1:quante_sez
        nomi_sezioni{ind}='NoName';
    end
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% AREE DRENATE
% mode operativo
if mode==1
    % load
    load([path_dati_input,nome_dominio,'\Aree_finali_',nome_dominio])
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% mode preparazione
else
    % calcolo delle aree drenate  per ciascuna sezione
    cd(path_codice)
    aree=aree_drenate(Punt_dominio,sezioni_indici_relativi);
    % Eliminazione aree drenate sovrapposte
    mappa_aree=zeros(size(Punt_dominio));
    L=cellfun(@length,aree);
    [ordinati,indici_sort]=sort(L);
    for i=length(L):-1:1
        valori=unique(mappa_aree(indici_sort(i)));
        mappa_aree(aree{indici_sort(i)})=i;
    end
    
    % verifico visivamente
    figure
    imagesc(mappa_aree)
    hold on
    [canalix,canaliy]=find(Choice_dominio==1);
    for indicew=1:length(canalix)
        plot(canaliy(indicew),canalix(indicew),'.k','markersize',6)
    end
    for indicew=1:quante_sez
        plot(sezioni_indici_relativi(indicew,2),sezioni_indici_relativi(indicew,1),'.r','markersize',20)
    end
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % modifica per allargare il dominio
    [righe,colonne]=size(mappa_aree);
    mappa_aree_allargata=mappa_aree;
    for indice=1:colonne
        temp=find(mappa_aree(:,indice)>0,1,'first');
        if isempty(temp)
        else
            if temp>1
                mappa_aree_allargata(temp-1,indice)=mappa_aree(temp,indice);
            end
        end
        clear temp
        temp=find(mappa_aree(:,indice)>0,1,'last');
        if isempty(temp)
        else
            if temp<righe
                mappa_aree_allargata(temp+1,indice)=mappa_aree(temp,indice);
            end
        end
        clear temp
    end
    for indice=1:righe
        temp=find(mappa_aree(indice,:)>0,1,'first');
        if isempty(temp)
        else
            if temp>1
                mappa_aree_allargata(indice,temp-1)=mappa_aree(indice,temp);
            end
        end
        clear temp
        temp=find(mappa_aree(indice,:)>0,1,'last');
        if isempty(temp)
        else
            if temp<colonne
                mappa_aree_allargata(indice,temp+1)=mappa_aree(indice,temp);
            end
        end
        clear temp
    end
    % modifica manuale EntellaCompleto
    if strcmp(nome_dominio,'EntellaCompleto')
        mappa_aree_allargata(57,27:40)=6;
        mappa_aree_allargata(58,24:40)=6;
        mappa_aree_allargata(59,21:41)=6;
        mappa_aree_allargata(60,18:42)=6;
        mappa_aree_allargata(61,17:43)=6;
        mappa_aree_allargata(62,16:44)=6;
        mappa_aree_allargata(63,15:45)=6;
        mappa_aree_allargata(64,14:46)=6;
    elseif strcmp(nome_dominio,'Entella')
        mappa_aree_allargata(24,8:15)=3;
        mappa_aree_allargata(25,6:15)=3;
        mappa_aree_allargata(26,4:16)=3;
        mappa_aree_allargata(27,3:17)=3;
        mappa_aree_allargata(28,2:18)=3;
        mappa_aree_allargata(29,1:19)=3;
    end
    % verifico visivamente
    figure
    imagesc(mappa_aree_allargata)
    hold on
    [canalix,canaliy]=find(Choice_dominio==1);
    for indicew=1:length(canalix)
        plot(canaliy(indicew),canalix(indicew),'.k','markersize',6)
    end
    for indicew=1:quante_sez
        plot(sezioni_indici_relativi(indicew,2),sezioni_indici_relativi(indicew,1),'.r','markersize',20)
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    % recupero info griglia metrica UTM32N da run fatti
    name_file_read=[path_dati_input,nome_dominio,'\',nome_hazmaps,'500',nome_hazmaps1];
    [A, R]=geotiffread(name_file_read);
    % rigriglio su griglia metrica UTM32N
    [new_x,new_y]=meshgrid(R.XWorldLimits(1):R.CellExtentInWorldX:R.XWorldLimits(2)-R.CellExtentInWorldX,...
        R.YWorldLimits(1):R.CellExtentInWorldY:R.YWorldLimits(2)-R.CellExtentInWorldY);
    mappa_aree_new=griddata(Lat_dominio_UTM32,Lon_dominio_UTM32,mappa_aree_allargata,new_y,new_x,'nearest');
%     % verifico visivamente
%     figure
%     imagesc(mappa_aree_new)
    % % salvo geotiff aree competenza
    % geotiffwrite(['prova_area',nome_dominio,'.tif'],double(mappa_aree_new),R, 'CoordRefSysCode',['EPSG:','32632'])
    % salvo file
    save([path_dati_input,nome_dominio,'\Aree_finali_',nome_dominio,'.mat'],'new_x','new_y',...
              'mappa_aree_new','R','mappa_aree_allargata','mappa_aree','Lat_dominio_UTM32','Lon_dominio_UTM32')
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% CALCOLO SCENARI: verifico lo scenario da associare alla portata assegnata su ogni sezione
% mode operativo
if mode==1
    % load
    % DA SCRIVERE
    portate=[400,450,170,1000,1250,1300]; % messo per ora
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% mode preparazione
else
    portate=[400,450,170,1000,1250,1300];
end

% calcolo scenari
for uuu=1:quante_sez
    TT(uuu)=round(exp(((Qindice_dominio(sezioni_indici_relativi(uuu,1),sezioni_indici_relativi(uuu,2)).*0.5239)+...
        portate(uuu))./(Qindice_dominio(sezioni_indici_relativi(uuu,1),sezioni_indici_relativi(uuu,2)).*1.0433)));
    disp(['sezione "',char(nomi_sezioni(uuu)),'": Portata=',num2str(portate(uuu)),' --> scenario=',num2str(TT(uuu))])
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% GENERAZIONE MAPPE: crezione degli scenari di unione
% dimensioni della griglia idraulica
[nrows,ncols]=size(mappa_aree_new);   
% cell array con gli indici matrice delle aree di competenza
for i=1:quante_sez
    indici_aree{i}=find(mappa_aree_new==i);                             
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
    mappa_flood(indici_aree{indici_T})=mappa_h((indici_aree{indici_T}));
    clear mappa_h
end
% definizione mappa finale
mappa_flood=double(mappa_flood)./1000;

% % verifica visiva (sconsigliata per domini grandi)
% figure
% pcolor(new_x,new_y,flipud(mappa_flood))
% shading flat
% caxis([0 7])
% hold on
% colormap([1 1 1;...
%           .8 1 1;...
%           .6 .94 1;...
%           .04 .96 .96;...
%           .04 .67 .96;...
%            0 .45 .74;...
%            0 0 1])
% for i=1:num_sezioni
%     plot(sezioni{i,5},sezioni{i,4},'.k','markersize',10)
% end

% scrittura geotiff finale
geotiffwrite([path_mappe_output,'\scenario_operativo-',nome_dominio,'.tif'],mappa_flood,R, 'CoordRefSysCode',['EPSG:','32632'])
disp('SCENARIO GENERATO!!!')









