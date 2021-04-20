%%%%% IMPORTANTE: quando sono confidente che funzioni correttamente,
%%%%% snellire lo script aggiungendo pi? input alla funzione


% script per il calcolo e la stima dell'indicatore sui dissesti
% P1 vs SM con P1 osservata nella prime 12h e prevista nelle successive 36h

function IndicatoreDissestiOperativo(sDataNow)

% input --> sDataNow = sino a quando ho le osservazioni di rain/melt

%% Path
sPathRoot='/share/work_matlab/drops/FloodProofs/';

% input statici Continuum
sPathLandData=[sPathRoot,'Continuum_Operativo/LandData/'];
% input mappe neve S3M
sPathSnowMap=[sPathRoot,'S3M_3.1_Nud_ARPA/S3MOutputMap/'];
% input melting previsto
sPathRainMelt=[sPathRoot,'Previsioni/VDA_6H/Input/Dati_meteo/RainDRiFt/'];
% output portate previsione vda 6h
sPathQVda6h=[sPathRoot,'Previsioni/OutputPortate/'];
% input umidit? Continuum
sPathMap=[sPathRoot,'Continuum_Operativo/Risultati/Mappe/'];

% output
sPathSintesi=[sPathRoot,'FigureCF/'];

%% lancio DropsInit
%cd('/share/work_matlab/drops/')
%DropsInit
%cd(sPathRoot)

%% carico Dem
load([sPathLandData,'DemVdA_SCA.mat'])
IInanDem=find(isnan(a2dDem)==1);

[iNRows iNCols]=size(a2dDem);

a2dDem(IInanDem)=NaN;

% Coordinate griglia sensori
dCellSize=0.00129110;

dLatMax=nanmax(nanmax(a2dLatDem));
dLatMin=nanmin(nanmin(a2dLatDem));
dLonMax=nanmax(nanmax(a2dLonDem));
dLonMin=nanmin(nanmin(a2dLonDem));

%% carico Aree Allertamento
a2dAA=arcgridread([sPathLandData,'AreeAllertamento.txt']);
a2dAA(IInanDem)=NaN;

aree=['B';'C';'A';'D'];% 1 2 3 4
nAree=length(aree);

IIaree=cell(1,4);
for iA=1:nAree
    IIaree{iA}=find(a2dAA==iA);
end

%% carico mappa CN per stimare Vmax
[a2dCN ref]=arcgridread([sPathLandData,'vda.cn.txt']);

a2dVMax=25.4.*(1000./a2dCN-10);

a2dVMax(IInanDem)=NaN;

%% Preparazione file di sintesi

%sDataNow=datestr(now,'yyyymmddHHMM');
sDataToday=[sDataNow(1:8),'0000'];

sNomeFile=([sPathSintesi,sprintf('SintesiIndicatoreDissestiOperativo.txt')]);
                                  
if exist(sNomeFile)~=2;
    
    flag=0;% file costruito ex novo
    
    fid2=fopen(sNomeFile,'w');
    fprintf(fid2,'Data P1(B) SM23gg-1(B) SM6gg(B) Reg(B) P1(C) SM23gg-1(C) SM6gg(C) Reg(C) P1(A) SM23gg-1(A) SM6gg(A) Reg(A) P1(D) SM23gg-1(D) SM6gg(D) Reg(D)\n');
    
    nDates=0;
    
    a1sData_txt=[];
    
    % files ante vuoti
    a2dMaxCum24h_pre=[];
    a2dMeanSM23_pre=[];
    a2dMeanSM6_pre=[];
    a1dRegSpace_pre=[];
    
    %sRainFiles=[];
    %sRainFiles=dir([sPathRainMelt,'Rain_*']);
    %sDataInizio=sRainFiles(1).name(6:(end-7));% leggo il primo file disponibile
    
    %sDataStart=sDataInizio;
    
else
    
    flag=1;% file esistente
    
    % leggo i giorni precedenti e aggiungo il nuovo giorno
    fid2=fopen(sNomeFile,'r');
    
    % lettura e preparazione del file.txt di aggiornamento
    oLine=fgetl(fid2);
    a2cData=textscan(fid2,'%s %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f');
    fclose(fid2);
    a1sData_txt=a2cData{1,1};
    a1dP1_B_txt=a2cData{1,2};a1dSM23_B_txt=a2cData{1,3};a1dSM6_B_txt=a2cData{1,4};a1dRegSpaceB_txt=a2cData{1,5}; % area B
    a1dP1_C_txt=a2cData{1,6};a1dSM23_C_txt=a2cData{1,7};a1dSM6_C_txt=a2cData{1,8};a1dRegSpaceC_txt=a2cData{1,9}; % area C
    a1dP1_A_txt=a2cData{1,10};a1dSM23_A_txt=a2cData{1,11};a1dSM6_A_txt=a2cData{1,12};a1dRegSpaceA_txt=a2cData{1,13}; % area A
    a1dP1_D_txt=a2cData{1,14};a1dSM23_D_txt=a2cData{1,15};a1dSM6_D_txt=a2cData{1,16};a1dRegSpaceD_txt=a2cData{1,17}; % area D
    
    a1sData_txt=char(a1sData_txt);
    
    [nDates nCfr]=size(a1sData_txt);
    
    %n_txt=datenum(str2double(a1sData_txt(nDates,1:4)),str2double(a1sData_txt(nDates,5:6)),str2double(a1sData_txt(nDates,7:8)),str2double(a1sData_txt(nDates,9:10)),str2double(a1sData_txt(nDates,11:12)),0);
    %sDataInizio=datestr(n_txt+1,'yyyymmddHHMM');
    
    fprintf('\n\nFile sintesi txt include da %s.%s.%s a %s.%s.%s\n',...
        a1sData_txt(1,1:4),a1sData_txt(1,5:6),a1sData_txt(1,7:8),...
        a1sData_txt(nDates,1:4),a1sData_txt(nDates,5:6),a1sData_txt(nDates,7:8));
    
    a2dMaxCum24h_pre=[a1dP1_B_txt a1dP1_C_txt a1dP1_A_txt a1dP1_D_txt];
    a2dMeanSM23_pre=[a1dSM23_B_txt a1dSM23_C_txt a1dSM23_A_txt a1dSM23_D_txt];
    a2dMeanSM6_pre=[a1dSM6_B_txt a1dSM6_C_txt a1dSM6_A_txt a1dSM6_D_txt];
    a1dRegSpace_pre=[a1dRegSpaceB_txt a1dRegSpaceC_txt a1dRegSpaceA_txt a1dRegSpaceD_txt];
    
    % riscrivo i dati nel file di testo
    fid2=fopen(sNomeFile,'w');
    fprintf(fid2,'Data P1(B) SM23gg-1(B) SM6gg(B) Reg(B) P1(C) SM23gg-1(C) SM6gg(C) Reg(C) P1(A) SM23gg-1(A) SM6gg(A) Reg(A) P1(D) SM23gg-1(D) SM6gg(D) Reg(D)\n');
    for iN=1:nDates
        fprintf(fid2,'%s %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f\n',...
            a1sData_txt(iN,:),a1dP1_B_txt(iN,:),a1dSM23_B_txt(iN,:),a1dSM6_B_txt(iN,:),a1dRegSpaceB_txt(iN,:),...
            a1dP1_C_txt(iN,:),a1dSM23_C_txt(iN,:),a1dSM6_C_txt(iN,:),a1dRegSpaceC_txt(iN,:),...
            a1dP1_A_txt(iN,:),a1dSM23_A_txt(iN,:),a1dSM6_A_txt(iN,:),a1dRegSpaceA_txt(iN,:),...
            a1dP1_D_txt(iN,:),a1dSM23_D_txt(iN,:),a1dSM6_D_txt(iN,:),a1dRegSpaceD_txt(iN,:));
    end
    
    fprintf('Run script estrazione/elaborazione variabili per oggi %s.%s.%s\n',...
        sDataToday(1,1:4),sDataToday(1,5:6),sDataToday(1,7:8));
    
end

sDataInizio=sDataToday;

%% Calcolo indicatore dissesti

Inizio=datenum(str2double(sDataInizio(1:4)),str2double(sDataInizio(5:6)),str2double(sDataInizio(7:8)),str2double(sDataInizio(9:10)),str2double(sDataInizio(11:12)),0);
Today=datenum(str2double(sDataToday(1:4)),str2double(sDataToday(5:6)),str2double(sDataToday(7:8)),str2double(sDataToday(9:10)),str2double(sDataToday(11:12)),0);

nDays=(round(Today-Inizio))+1;

a2dMaxCum24h=nan(nDays,nAree);
sDataInizioMaxCum24h=cell(nDays,nAree);
a2dMeanSM23=nan(nDays,nAree);
a2dMeanSM6=nan(nDays,nAree);
a1dRegSpace=nan(nDays,nAree);

t=0;a1sDateVetTot=cell(nDays,1);
sData=sDataInizio;
sDataFine=sDataToday;% coincidono perch? run solo di oggi

while str2double(sData)<=str2double(sDataFine)
    
    t=t+1;
    
    % caratterizzo P1 e SM del giorno considerato
    fprintf('\ngiorno %s.%s.%s \n',sData(7:8),sData(5:6),sData(1:4))
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% determino il grado di saturazione medio giornaliero sulle AA %%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    n=datenum(str2double(sData(1:4)),str2double(sData(5:6)),str2double(sData(7:8)),str2double(sData(9:10)),str2double(sData(11:12)),0);
    
    %% SM alle 23UTC giorno prima (per i grafici)
    sDataSM23=datestr(n-1/24,'yyyymmddHHMM');
    
    fprintf('     SM23gg-1: %s.%s UTC - %s.%s.%s \n',sDataSM23(9:10),sDataSM23(11:12),sDataSM23(7:8),sDataSM23(5:6),sDataSM23(1:4));
    
    a2dMap=nan(iNRows,iNCols);
    sNomeMappa=[sPathMap,'vdaV_',sDataSM23];
    system(['gunzip ',sNomeMappa,'.gz']);
    fid=fopen(sNomeMappa);
    a2dMap=fread(fid,[iNRows iNCols],'int32');
    fclose(fid);
    system(['gzip ',sNomeMappa]);
    a2dMap=double(a2dMap./10000);
    
    a2dMap(IInanDem)=NaN;
    
    a2dS=zeros(iNRows,iNCols);
    a2dS=a2dMap./a2dVMax;
    
    a2dS(a2dS>1)=1;
    a2dS(a2dS<0)=0;
    a2dS(IInanDem)=NaN;
    
    %% SM alle 6UTC giorno corrente (per file.txt)
    sDataSM6=datestr(n+6/24,'yyyymmddHHMM');
    
    fprintf('     SM6hgg: %s.%s UTC - %s.%s.%s \n',sDataSM6(9:10),sDataSM6(11:12),sDataSM6(7:8),sDataSM6(5:6),sDataSM6(1:4));
    
    a2dMap=nan(iNRows,iNCols);
    sNomeMappa=[sPathMap,'vdaV_',sDataSM6];
    system(['gunzip ',sNomeMappa,'.gz']);
    fid=fopen(sNomeMappa);
    a2dMap=fread(fid,[iNRows iNCols],'int32');
    fclose(fid);
    system(['gzip ',sNomeMappa]);
    a2dMap=double(a2dMap./10000);
    
    a2dMap(IInanDem)=NaN;
    
    a2dS6=zeros(iNRows,iNCols);
    a2dS6=a2dMap./a2dVMax;
    
    a2dS6(a2dS6>1)=1;
    a2dS6(a2dS6<0)=0;
    a2dS6(IInanDem)=NaN;
    
    for iA=1:nAree % 1=B; 2=C; 3=A; 4=D;
        
        fprintf('           Stima SM su area %s \n',aree(iA,1));
        
        if strcmp(sDataSM23(5:6),'07')==1 || strcmp(sDataSM23(5:6),'08')==1 || strcmp(sDataSM23(5:6),'09')==1 || strcmp(sDataSM23(5:6),'10')==1
            % estraggo dato medio sull'area senza mascherare la mappa di V0 con quella di SWE
            iiS=[];
            iiS=a2dS(IIaree{iA});
            a2dMeanSM23(t,iA)=nanmean(iiS);
            
            iiS=[];
            iiS=a2dS6(IIaree{iA});
            a2dMeanSM6(t,iA)=nanmean(iiS);
            
            fprintf('              Senza Maschera Neve (luglio, agosto, settembre) \n');
        else
            % carico mappa di SWE
            a2dSWE=nan(iNRows,iNCols);
            sNomeMappa=[sPathSnowMap,'SWE_',sDataSM23];
            system(['gunzip ',sNomeMappa,'.out.gz']);
            fid=fopen([sNomeMappa,'.out']);
            a2dSWE=fread(fid,[iNRows iNCols],'single');
            fclose(fid);
            system(['gzip ',sNomeMappa,'.out']);
            
            a2dSWE(a2dSWE<10)=0;
            a2dSWE(IInanDem)=NaN;
            
            a2dS(a2dSWE>0)=NaN;
            a2dS6(a2dSWE>0)=NaN;
            
            % 23 utc gg-1: maschero la mappa di V0 con quella di SWE
            iiS=[];
            iiS=a2dS(IIaree{iA});
            a2dMeanSM23(t,iA)=nanmean(iiS);
            
            iiSWE=[];
            iiSWE=a2dSWE(IIaree{iA});
            percS=[];
            percS=round(100*(length(find(iiSWE==0))./length(iiS)));
            
            if percS<5
                a2dMeanSM23(t,iA)=NaN;
            end
            
            fprintf('              Con Maschera Neve: SM stimata su %d%% zona di allerta \n',percS);
            
            % 6 utc gg
            iiS=[];
            iiS=a2dS6(IIaree{iA});
            a2dMeanSM6(t,iA)=nanmean(iiS);
            
            iiSWE=[];
            iiSWE=a2dSWE(IIaree{iA});
            percS=[];
            percS=round(100*(length(find(iiSWE==0))./length(iiS)));
            
            if percS<5
                a2dMeanSM6(t,iA)=NaN;
            end
            
        end
        
        if isnan(a2dMeanSM23(t,iA))==1
            fprintf('              Attenzione SM=NaN in zona %s per totale copertura nevosa\n',aree(iA,1))
        end
        
    end
    
    fprintf('     stimata SM \n');
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% determino la pioggia media giornaliera sulle AA (come peggior cumulata su 24h delle 48h) %%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    sDataInizioOss=datestr(n,'yyyymmddHHMM'); % 00.00 UTC gg
    inizioOss=datenum(str2double(sDataInizioOss(1:4)),str2double(sDataInizioOss(5:6)),str2double(sDataInizioOss(7:8)),str2double(sDataInizioOss(9:10)),str2double(sDataInizioOss(11:12)),0);
    
    if str2double(sData)==str2double(sDataFine) % oggi
        
        sDataFineOss=sDataNow;
        fineOss=datenum(str2double(sDataFineOss(1:4)),str2double(sDataFineOss(5:6)),str2double(sDataFineOss(7:8)),str2double(sDataFineOss(9:10)),str2double(sDataFineOss(11:12)),0);
        
        fprintf('\n Anticipo previsione stimato da orario Run\n');
        
    else % giorni precedenti
        
        % se trovo il file
        sQFiles=[];
        sQFiles=dir([sPathQVda6h,'Q_VDA_6H_*_',sData,'*']);
        
        if isempty(sQFiles)~=1
            sDataFineOss=sQFiles(1).name(10:21);% leggo il primo file disponibile
            fineOss=datenum(str2double(sDataFineOss(1:4)),str2double(sDataFineOss(5:6)),str2double(sDataFineOss(7:8)),str2double(sDataFineOss(9:10)),str2double(sDataFineOss(11:12)),0);
        
            fprintf('\n Anticipo previsione letto da file.mat (orario Run giorni scorsi) \n');
            
        else
            % pohi casi in cui ? saltato il run previsioni soggettive vda_6h
            fineOss=(inizioOss+9/24);
            sDataFineOss=datestr(fineOss,'yyyymmddHHMM');
            
            fprintf('\n Anticipo previsione imposto di 3h (manca file.mat vecchia previsione) \n')
            
        end
    end
    
    sDataInizioPrev=datestr(fineOss+1/24,'yyyymmddHHMM');
    
    % anticipo rispetto alle 12.00 UTC
    anticipo=round(12-(((fineOss-inizioOss)*24)+1));
    
    sDataFinePrev=datestr(n+47/24,'yyyymmddHHMM'); % 23.00 UTC gg+1
    
    %% intervallo OSSERVATO (pioggia liquida + fusione nevosa)
            
    dTimeOss=[];
    dTimeOss=round(((fineOss-inizioOss)*24)+1); % 12ore di osservazioni
    
    fprintf('           Stima Osservazioni sulle aree\n');
    
    sDataT=sDataInizioOss;
    tOss=0; a1sDateVetOss=cell(dTimeOss,1);
    a2dOss=nan(dTimeOss,nAree);
    while str2double(sDataT)<=str2double(sDataFineOss)
        
        tOss=tOss+1;
        
        a2dMapRainMelt=nan(iNRows,iNCols);
        sNomeMappa=[sPathSnowMap,'Rain_',sDataT];
        system(['gunzip ',sNomeMappa,'.out.gz']); % De-compressione della mappa
        fid=fopen([sNomeMappa,'.out']);
        a2dMapRainMelt=fread(fid,[iNRows iNCols],'single');
        fclose(fid);
        system(['gzip ',sNomeMappa,'.out']);
        
        a2dMapRainMelt=single(a2dMapRainMelt);
        a2dMapRainMelt(IInanDem)=NaN;
        
        for iA=1:nAree % 1=B; 2=C; 3=A; 4=D;
            iiT=[];
            iiT=a2dMapRainMelt(IIaree{iA});
            a2dOss(tOss,iA)=nanmean(iiT); % rain + melting
        end
        
        a1sDateVetOss{tOss}=sDataT;
        
        n=datenum(str2double(sDataT(1:4)),str2double(sDataT(5:6)),str2double(sDataT(7:8)),str2double(sDataT(9:10)),str2double(sDataT(11:12)),0);
        sDataT=datestr(n+1/24,'yyyymmddHHMM');
    end
    
    a1sDateVetOss=char(a1sDateVetOss);
    
    fprintf('           Stimate Osservazioni\n');
    
    %% estraggo previsioni soggettive sulla finestra di 36h e preparo le mappe di pioggia  
    
    fprintf('           Estraggo previsioni vda6h del %s\n',sData);
        
    a1sAreeAll=char('Vda-B','Vda-C','Vda-A','Vda-D');
    
    fprintf('\n%s: previsione CON anticipo\n',sData(1:8));
    a2dMedia=nan(4,7);a2dQZT=nan(4,7);a2dQLN=nan(4,7);
    sDataYesterday=datestr(n-1,'yyyymmddHHMM');
    
    for iJ=1:4
        
        sSubRegionName=deblank(a1sAreeAll(iJ,:));
        
        [a1dPrevSogg]= GetPreviByVariable_new (sDataYesterday(1:8),[sDataYesterday(1:8),'1200'],'Precip 6h med',sSubRegionName);
        a2dMedia(iJ,1)=str2double(cell2mat(a1dPrevSogg(4,2)));
        a1dPrevSogg=[];
        [a1dPrevSogg]= GetPreviByVariable_new (sData(1:8),[sData(1:8),'1200'],'Precip 6h med',sSubRegionName);
        
        % se non trovo la previ di oggi esco dallo script
        if iscell(a1dPrevSogg)==0
            fprintf('\nAncora assente previsione di oggi\n')
            a2dMedia(iJ,2:7)=[];
            fprintf('\nEsco dal run Indicatore Dissesti Operativo\n')
        else
            a2dMedia(iJ,2:7)=[str2double(cell2mat(a1dPrevSogg(1,2))),str2double(cell2mat(a1dPrevSogg(2,2))),str2double(cell2mat(a1dPrevSogg(3,2))),str2double(cell2mat(a1dPrevSogg(4,2))),str2double(cell2mat(a1dPrevSogg(5,2))),str2double(cell2mat(a1dPrevSogg(6,2)))];
            fprintf('\nPresente previsione di oggi (Pioggia)\n')            
        end
        
        [a1dPrevSogg]= GetPreviByVariable_new(sDataYesterday(1:8),[sDataYesterday(1:8),'1200'],'Zero termico',sSubRegionName);
        a2dQZT(iJ,1)=str2double(cell2mat(a1dPrevSogg(2,2)));
        a1dPrevSogg=[];
        [a1dPrevSogg]= GetPreviByVariable_new(sData(1:8),[sData(1:8),'1200'],'Zero termico',sSubRegionName);
        
        % se non trovo la previ di oggi esco dallo script
        if iscell(a1dPrevSogg)==0
            fprintf('\nAncora assente previsione di oggi\n')
            a2dQZT(iJ,2:7)=[];
            fprintf('\nEsco dal run Indicatore Dissesti Operativo\n')
        else
            a2dQZT(iJ,2:7)=[str2double(cell2mat(a1dPrevSogg(1,2))),str2double(cell2mat(a1dPrevSogg(1,2))),str2double(cell2mat(a1dPrevSogg(2,2))),str2double(cell2mat(a1dPrevSogg(2,2))),str2double(cell2mat(a1dPrevSogg(3,2))),str2double(cell2mat(a1dPrevSogg(3,2)))];
            fprintf('\nPresente previsione di oggi (Zero Termico)\n') 
        end
        
        [a1dPrevSogg]= GetPreviByVariable_new(sDataYesterday(1:8),[sDataYesterday(1:8),'1200'],'Quota neve',sSubRegionName);
        a2dQLN(iJ,1)=str2double(cell2mat(a1dPrevSogg(2,2)));
        a1dPrevSogg=[];
        [a1dPrevSogg]= GetPreviByVariable_new(sData(1:8),[sData(1:8),'1200'],'Quota neve',sSubRegionName);
        
        % se non trovo la previ di oggi esco dallo script
        if iscell(a1dPrevSogg)==0
            fprintf('\nAncora assente previsione di oggi\n')
            a2dQLN(iJ,2:7)=[];
            fprintf('\nEsco dal run Indicatore Dissesti Operativo\n')
        else
            a2dQLN(iJ,2:7)=[str2double(cell2mat(a1dPrevSogg(1,2))),str2double(cell2mat(a1dPrevSogg(1,2))),str2double(cell2mat(a1dPrevSogg(2,2))),str2double(cell2mat(a1dPrevSogg(2,2))),str2double(cell2mat(a1dPrevSogg(3,2))),str2double(cell2mat(a1dPrevSogg(3,2)))];
            fprintf('\nPresente previsione di oggi (Quota neve)\n') 
        end
        
        clear sSubRegionName
    end
    
    % dove QLN=NaN, QLN=QZT
    a2dQLN(isnan(a2dQLN)==1)=a2dQZT(isnan(a2dQLN)==1);
    
    %% previsione da scala temporale 6h a 1h
    fprintf('           Stima Previsioni sulle aree\n');
    
    dTimePrev=round(anticipo+36);
    
    sDataP=sDataInizioPrev;
    
    tPrev=0; a1sDateVetPrev=[];a1sDateVetPrev=cell(dTimePrev,1);
    a2dRainPrev=[];a2dRainPrev=nan(dTimePrev,nAree);
    a2dMeltPrev=[];a2dMeltPrev=nan(dTimePrev,nAree);
    while str2double(sDataP)<=str2double(sDataFinePrev)
        
        tPrev=tPrev+1;
        if tPrev<=anticipo
            step=1;
        else
            step=(ceil((tPrev-anticipo)/6))+1;
        end
        
        % creo mappa di pioggia prevista
        for iA=1:nAree
            
            a2dMapRainPrevTemp=nan(iNRows,iNCols);
            a2dMapRainPrevTemp(IIaree{iA})=a2dMedia(iA,step)/6;
            a2dDemTemp=nan(iNRows,iNCols);
            a2dDemTemp(IIaree{iA})=a2dDem(IIaree{iA});
            
            % ritaglio mappa Rain prevista sulla QLN prevista
            overQLN=[];
            overQLN=find(a2dDemTemp>a2dQLN(iA,step));
            a2dMapRainPrevTemp(overQLN)=0;
            
            iiT=[];
            iiT=a2dMapRainPrevTemp(IIaree{iA});
            a2dRainPrev(tPrev,iA)=nanmean(iiT);
            
        end
                
        % letta mappa di fusione prevista
        a2dMapMeltPrev=nan(iNRows,iNCols);
        sNomeMappa=[sPathRainMelt,'Melting_',sDataP];
        
        
        if exist([sNomeMappa,'.out.gz'])==2
            system(['gunzip ',sNomeMappa,'.out.gz']); % De-compressione della mappa
            fid=fopen([sNomeMappa,'.out']);
            a2dMapMeltPrev=fread(fid,[iNRows iNCols],'single');
            fclose(fid);
            system(['gzip ',sNomeMappa,'.out']);
            
        else
            fprintf('\nAttenzione: assente fusione prevista!\n')
            a2dMapMeltPrev=[];
            
        end
        
        a2dMapMeltPrev=single(a2dMapMeltPrev);
        a2dMapMeltPrev(IInanDem)=NaN;
        
        for iA=1:nAree % 1=B; 2=C; 3=A; 4=D;
            iiT=[];
            iiT=a2dMapMeltPrev(IIaree{iA});
            a2dMeltPrev(tPrev,iA)=nanmean(iiT);
        end
        
        a1sDateVetPrev{tPrev}=sDataP;
        
        n=datenum(str2double(sDataP(1:4)),str2double(sDataP(5:6)),str2double(sDataP(7:8)),str2double(sDataP(9:10)),str2double(sDataP(11:12)),0);
        sDataP=datestr(n+1/24,'yyyymmddHHMM');
    end
    
    a1sDateVetPrev=char(a1sDateVetPrev);
    
    fprintf('           Stimate Previsioni\n');
    
    % vettore tempi completo
    a1sDateVet=[a1sDateVetOss;a1sDateVetPrev];
    
    % matrice completa oss+prev (rain+melt)
    iin=find(isnan(a2dRainPrev)==1);
    a2dRainPrev(iin)=0;
    a2dMeanOssPrev=[a2dOss;a2dRainPrev+a2dMeltPrev];
    
    %% stimo la peggior cumulata di 24h sulle 48h considerate
    for iA=1:nAree
        
        fprintf('           Stima P1 su area %s \n',aree(iA,1));
        
        a1dMeanOssPrevArea=nan(48,1);% precipitazione totale
        a1dMeanOssPrevArea=a2dMeanOssPrev(:,iA);
        a1dMeanOssPrevArea=a1dMeanOssPrevArea';
        
        ik=0;
        a1dCum24h=[];
        for time=24:48
            ik=ik+1;
            a1dCum24h(ik,1)=nansum(a1dMeanOssPrevArea(1,time-23:time));
        end
        a1dCum24h=[nan(23,1);a1dCum24h];
        iI=[];
        iI=find(a1dCum24h==nanmax(a1dCum24h));
        a2dMaxCum24h(t,iA)=a1dCum24h(iI(1)); % precipitazione totale
        
        % tengo traccia dell'inizio delle peggior cumulata su 24h
        sDataInizioMaxCum24h{t,iA}=a1sDateVet(iI(1),:);
        
    end
    
    fprintf('     Stimata P1 \n');
    
    %% determino regione dello spazio dello scenario odierno
    
    for i=1:nAree % B C A D
        
        % rette R1 - R2
        a1=[];b1=[];
        if i==1;a1=-192;b1=120;end;%%%area B
        if i==2;a1=-158;b1=100;end;%%%area C
        if i==3;a1=-142;b1=90;end;%%%area A
        if i==4;a1=-142;b1=90;end;%%%area D
        
        % rette R3-R4
        if i==1;a2=-90;b2=95;end;%%%area B
        if i==2;a2=-37.5;b2=42.5;end;%%%area C
        if i==3;a2=-40;b2=45;end;%%%area A
        if i==4;a2=-37.5;b2=42.5;end;%%area D
        
        % rette R1-R4
        a3=-7.5;b3=9.5;
        
        % definisco regione dello spazio
        if i==3 || i==1 % aree B e A
            if a2dMeanSM23(t,i)<0.5   % R1 - R2
                if a2dMaxCum24h(t,i)<a1.*a2dMeanSM23(t,i)+b1
                    a1dRegSpace(t,i)=1;
                else
                    a1dRegSpace(t,i)=2;
                end
            else
                if a2dMeanSM23(t,i)>0.6   % R1 - R4 - R3
                    if a2dMaxCum24h(t,i)>a2.*a2dMeanSM23(t,i)+b2   % R3 - R4
                        a1dRegSpace(t,i)=3;
                    else
                        if a2dMaxCum24h(t,i)>a3.*a2dMeanSM23(t,i)+b3 % R4 - R1
                            a1dRegSpace(t,i)=4;
                        else
                            a1dRegSpace(t,i)=1;
                        end
                    end
                else
                    if a2dMaxCum24h(t,i)>a2.*a2dMeanSM23(t,i)+b2   % R3 - R4
                        a1dRegSpace(t,i)=3;
                    else
                        if a2dMaxCum24h(t,i)>a1.*a2dMeanSM23(t,i)+b1 % R4 - R1
                            a1dRegSpace(t,i)=4;
                        else
                            a1dRegSpace(t,i)=1;
                        end
                    end
                end
            end
        else % altre aree
            if a2dMeanSM23(t,i)<0.6   % R1 - R2
                if a2dMaxCum24h(t,i)<a1.*a2dMeanSM23(t,i)+b1
                    a1dRegSpace(t,i)=1;
                else
                    a1dRegSpace(t,i)=2;
                end
            else   % R1 - R4 - R3
                if a2dMaxCum24h(t,i)>a2.*a2dMeanSM23(t,i)+b2   % R3 - R4
                    a1dRegSpace(t,i)=3;
                else
                    if a2dMaxCum24h(t,i)>a3.*a2dMeanSM23(t,i)+b3 % R4 - R1
                        a1dRegSpace(t,i)=4;
                    else
                        a1dRegSpace(t,i)=1;
                    end
                end
            end
        end
    end
    
    %% inserimento dati aggiornati file.txt
    fprintf(fid2,'%s %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f %1.1f %1.2f %1.2f %1.0f\n',sData,...
        a2dMaxCum24h(t,1),a2dMeanSM23(t,1),a2dMeanSM6(t,1),a1dRegSpace(t,1),...
        a2dMaxCum24h(t,2),a2dMeanSM23(t,2),a2dMeanSM6(t,2),a1dRegSpace(t,2),...
        a2dMaxCum24h(t,3),a2dMeanSM23(t,3),a2dMeanSM6(t,3),a1dRegSpace(t,3),...
        a2dMaxCum24h(t,4),a2dMeanSM23(t,4),a2dMeanSM6(t,4),a1dRegSpace(t,4));
    
    a1sDateVetTot{t}=sData(1:8);
    
    fprintf('Completato giorno %s.%s.%s \n\n\n',sData(7:8),sData(5:6),sData(1:4))
    
    n=datenum(str2double(sData(1:4)),str2double(sData(5:6)),str2double(sData(7:8)),str2double(sData(9:10)),str2double(sData(11:12)),0);
    sData=datestr(n+1,'yyyymmddHHMM');
    
end

fclose(fid2);

a1sDateVetTot=char(a1sDateVetTot);

a1sDateVetTot=[a1sData_txt(:,1:8);a1sDateVetTot];

% p.ti totali
nDaysTot=nDates+nDays;

a2dMaxCum24h=[a2dMaxCum24h_pre;a2dMaxCum24h];
a2dMeanSM23=[a2dMeanSM23_pre;a2dMeanSM23];
a2dMeanSM6=[a2dMeanSM6_pre;a2dMeanSM6];
a1dRegSpace=[a1dRegSpace_pre;a1dRegSpace];

%% definisco percorso salvataggio figure
sPathFigure=[sPathSintesi,sDataNow(1:8),'/'];mkdir(sPathFigure);

% salvataggio di sicurezza file.txt
copyfile(sNomeFile,sPathFigure);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Figure indicatore dissesti %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

scrsz = get(0,'ScreenSize');
figure('Position',[scrsz(1) scrsz(2) scrsz(3) scrsz(4)]);

fprintf('plot scenari precedenti incluso oggi %s.%s\n',sDataFine(1,7:8),sDataFine(1,5:6))

% grafico solo i punti degli ultimi 3 mesi (90 gg)
if nDaysTot>90
    inGr=nDaysTot-90;
else
    inGr=1;
end

for iN=inGr:nDaysTot

    for i=1:nAree % B C A D
        
        s(i)=subplot(2,2,i);
        hold on
        
        % componenti grafiche che devono stare sotto agli scenari (pallini) 
        if iN==nDaysTot
          
            % rette di regressione
            pos=[];
            if aree(i)=='A';pos=3;end
            if aree(i)=='B';pos=1;end
            if aree(i)=='C';pos=2;end
            if aree(i)=='D';pos=4;end
            
            s(i)=subplot(2,2,i);
            
            s(pos)=subplot(2,2,pos);
            
            a1dX=[];a1dYregr=[];
            a=[];b=[];
            if pos==1;a1dX=(0:0.1:0.6);a=-192;b=120;end;
            if pos==2;a1dX=(0:0.1:0.6);a=-158;b=100;end;
            if pos==3;a1dX=(0:0.1:0.6);a=-142;b=90;end;
            if pos==4;a1dX=(0:0.1:0.6);a=-142;b=90;end;
            a1dYregr=a.*a1dX+b;
            xmin=[];
            xmin=a1dYregr(end);
            
            hold on
            plot(a1dX,a1dYregr,'g--','Linewidth',1)
            if pos==1
                plot([0.5 0.5],[24 200],'g--','Linewidth',1)
            elseif pos==3
                plot([0.5 0.5],[20 200],'g--','Linewidth',1)
            else
                plot([0.6 0.6],[xmin 200],'g--','Linewidth',1)
            end
            
            title(sprintf('Area %s ',aree(i)),'Fontsize',8);
            
            a1dX2=[];a1dYregr2=[];
            a1=[];b1=[];
            if pos==1;a1dX2=(0.5:0.1:1);a1=-90;b1=95;end;%%%area B
            if pos==2;a1dX2=(0.6:0.1:1);a1=-37.5;b1=42.5;end;%%%area C
            if pos==3;a1dX2=(0.5:0.1:1);a1=-40;b1=45;end;%%%area A
            if pos==4;a1dX2=(0.6:0.1:1);a1=-37.5;b1=42.5;end;%%area D
            a1dYregr2=a1.*a1dX2+b1;
            plot(a1dX2,a1dYregr2,'g--','Linewidth',1)
            if pos==3
                plot([0.6 1],[5 2],'g--','Linewidth',1)
            else
                plot([0.6 1],[5 2],'g--','Linewidth',1)
            end
            
            % etichette regioni dello spazio
            if i==1 %B
                text(0.15,50,sprintf('R1'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.25,150,sprintf('R2'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.75,125,sprintf('R3'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.6,20,sprintf('R4'),'FontSize',9,'Color',[139 139 131]./255);
            else % altre aree
                text(0.15,30,sprintf('R1'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.25,80,sprintf('R2'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.75,70,sprintf('R3'),'FontSize',9,'Color',[139 139 131]./255);
                text(0.7,10,sprintf('R4'),'FontSize',9,'Color',[139 139 131]./255);
            end
            hold on
        end
        
        if iN==nDaysTot % giorno di oggi
            % plot scenario giornaliero
            plot(a2dMeanSM23(iN,i),a2dMaxCum24h(iN,i),'o','Linewidth',0.2,'MarkerSize',8,'MarkerEdgeColor',[0 0 0]./255,'MarkerFaceColor',[139 139 131]./255);
            hold on
            text(a2dMeanSM23(iN,i)+0.004,a2dMaxCum24h(iN,i)+1,sprintf('%s.%s.%s\n    (R%d)\n',a1sDateVetTot(iN,7:8),a1sDateVetTot(iN,5:6),a1sDateVetTot(iN,1:4),a1dRegSpace(iN,i)),'FontSize',5);
            
        else % plot degli scenari precedenti
            plot(a2dMeanSM23(iN,i),a2dMaxCum24h(iN,i),'o','Linewidth',0.2,'MarkerSize',5,'MarkerEdgeColor',[180 180 180]./255,'MarkerFaceColor',[180 180 180]./255);
            hold on
        end
        
        hold on
        
        if iN==nDaysTot
            
            % componenti grafiche 
            xlim([0 1])
            set(gca,'XTickLabel',(0:0.2:1),'FontSize',9)
            if i==1 % area B
                ylim([0 200])
                set(gca,'YTickLabel',(0:50:200),'FontSize',9)
            else % altre aree
                ylim([0 100])
                set(gca,'YTickLabel',(0:20:100),'FontSize',9)
            end
            
            grid on
            xlabel('Sat Deg [-]','FontSize',7);
            ylabel('P1 [mm]','FontSize',7);
            
            hold on
            
            if isnan(a2dMeanSM23(iN,i))==1
                if i==1% area B
                    text(0.3,130,sprintf('Scenario odierno\n     ASSENTE;\n zona totalmente\n coperta da neve'),'FontSize',11);
                else
                    text(0.3,60,sprintf('Scenario odierno\n     ASSENTE;\n zona totalmente\n coperta da neve'),'FontSize',11);
                end
            end
            
        end
        
    end
end

hold off

spt=suptitle(sprintf('Indicatore dissesti previsto dal %s.%s.%s al  %s.%s.%s (ultimi 3 mesi)',...
    a1sDateVetTot(inGr,7:8),a1sDateVetTot(inGr,5:6),a1sDateVetTot(inGr,1:4),...
    a1sDateVetTot(nDaysTot,7:8),a1sDateVetTot(nDaysTot,5:6),a1sDateVetTot(nDaysTot,1:4)));
set(spt,'FontSize',12);

an=annotation('textbox',[0.3 0.843 0.5 0.1],'String',sprintf('Scenario odierno basato su previsione soggettiva a 6h del %s.%s.%s',a1sDateVetTot(nDaysTot,7:8),a1sDateVetTot(nDaysTot,5:6),a1sDateVetTot(nDaysTot,1:4)),'LineStyle','none','FontAngle','italic');
set(an,'FontSize',8.5);

% salvataggio
sNomeFile=[sPathFigure,'Indicatore_dissesti_',sDataFine(1:8)];
saveas(gcf,[sNomeFile,'.fig'],'fig');
saveas(gcf,[sNomeFile,'.png'],'png');
