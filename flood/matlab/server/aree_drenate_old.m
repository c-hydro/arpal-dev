function aree=aree_drenate(pnt,sezioni)



% aree=aree_drenate(pnt,sezioni)
%
% Ricostruisce le aree drentate da ogni sezione a partire dal raster dei
% puntatori idrologici, secondo i seguenti codici:
% 32 64 128
% 16  0   1
%  8  4   2
%
% INPUT:
%   pnt = raster dei puntatori
%   sezioni = matrice che contiene nelle prime due colonne gli indici i e j
%             delle sezioni a monte delle quali vanno ricostruite le aree
% OUTPUT:
%   aree = cell array in ogni elemento del quale c'e' un vettore degli
%          indici assoluti dei pixel appartenenti alla data area


% eliminazione dati mancanti
pnt(pnt<0)=NaN;
% pnt=flipud(pnt);
[n,m]=size(pnt);
[n_orig,m_orig]=size(pnt); %#ok<ASGLU>


% matrici ausiliarie
M=NaN(n+2,m+2);
M(2:end-1,2:end-1)=pnt;
pnt=M;
[n,m]=size(pnt);
di=ones(3,1)*[-1 0 1];
dj=[-1;0;1]*ones(1,3);
di=di(:);
dj=dj(:);
% dd=[2;1;128;4;0;64;8;16;32];
dd=[3;6;9;2;0;8;1;4;7];



% ricostruzione aree
N=size(sezioni,1);
elenco_sezioni=zeros(1,N);
for i=1:N
    elenco_sezioni(i)=sub2ind([n,m],sezioni(i,1)+1,sezioni(i,2)+1);
end
aree=cell(1,length(elenco_sezioni));
h=waitbar(0);
for s=1:length(elenco_sezioni)
    p=elenco_sezioni(s);
    area=p;
    punti_da_esam=p;
    area_old_cell=cell(1,4);
    area_old_cell{1}=area;
    for ic=2:length(area_old_cell)
        area_old_cell{ic}=ic;
    end
    while isempty(punti_da_esam)==0
        punti_nuovi=[];
        for i=1:length(punti_da_esam)
            p=punti_da_esam(i);
            [pxy(1),pxy(2)]=ind2sub([n,m],p);
            punti_intorno=[pxy(1)+di,pxy(2)+dj];
            punti_intorno=[reshape(reshape(punti_intorno(:,1),3,3)',9,1),reshape(reshape(punti_intorno(:,2),3,3)',9,1)];
            i_punti_intorno=sub2ind([n,m],punti_intorno(:,1),punti_intorno(:,2));
            punti_nuovi=[punti_nuovi,(i_punti_intorno((pnt(i_punti_intorno)-dd)==0))']; %#ok<AGROW>
        end
        punti_nuovi=unique([punti_nuovi,setdiff(punti_nuovi,area)]);
        area=unique([area,punti_nuovi]);
        punti_da_esam=punti_nuovi;
        if (length(area_old_cell{1})==length(area_old_cell{2}) && length(area_old_cell{2})==length(area_old_cell{3}) && length(area_old_cell{3})==length(area_old_cell{4}))
            if (all(area_old_cell{1}==area_old_cell{2}) && all(area_old_cell{2}==area_old_cell{3}) && all(area_old_cell{3}==area_old_cell{4}))
                break
            end
        end
        for ic=length(area_old_cell):-1:2
            area_old_cell{ic}=area_old_cell{ic-1};
        end
        area_old_cell{1}=area;
    end
    % conversione delle coordinate sulla griglia originale
    [i_area,j_area]=ind2sub([n,m],area);
    i_area=i_area-1;
    j_area=j_area-1;
    i_area=(n-2)-i_area+1;
    area=sub2ind([n-2,m-2],n_orig-i_area+1,j_area);
    aree{s}=area;
    waitbar(s/length(elenco_sezioni),h);
end
close(h);
