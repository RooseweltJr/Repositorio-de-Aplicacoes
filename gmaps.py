import pandas as pd
import googlemaps
import numpy as np

class gmaps_dist:
    def __init__(self, key: str, proxies=None):
        self.gmaps = self.configurar_api(key, proxies)

    def configurar_api(self, key: str, proxies:None):
        if proxies is None:
            gmaps = googlemaps.Client(key=key)
        else:
            gmaps = googlemaps.Client(key=key, requests_kwargs={'proxies': proxies})
        return gmaps

    def unir_df(df_dist: pd.DataFrame, df_dur: pd.DataFrame) -> pd.DataFrame:
        print(f'\n Agrupando dados')
        df_combined = pd.concat([df_dist, df_dur], axis=1)
        colunas_alternadas = [col for pair in zip(df_dist.columns, df_dur.columns) for col in pair]
        df_final = df_combined[colunas_alternadas]
        return df_final

    def criar_rotulos(rot_possib: list):
        rot_possib_dist = ['Distância - ' + r + ' (Km)' for r in rot_possib]
        rot_possib_time = ['Duração - ' + r + ' (h)' for r in rot_possib]
        return rot_possib_dist, rot_possib_time

    def distancia_tempo(self, origins: str, destination: str):
        
        ''' Monta o link da consulta para o arquivo Json e extrai a *distance* e *duration*

        - **Entrada**: Coordenadas de origem e destino ('lat,long') em string;

        - **Saída**: Distancia em Km e tempo em Horas'''

        try:
            resultado_json = self.gmaps.distance_matrix(origins, destination, mode='driving')
            distancia = resultado_json["rows"][0]['elements'][0]['distance']['value'] / 1000
            tempo = resultado_json["rows"][0]['elements'][0]['duration']['value'] / 3600
            return distancia, tempo
        except:
            return 0, 0

    def calcular_distancias(self, df_mutiplo: pd.DataFrame, coluna_nome_multipla: str, coluna_coord_multipla: str,
                            df_possib: pd.DataFrame, coluna_nome_possib: str, coluna_coord_possib: str,
                            destination: bool = True) -> pd.DataFrame:
        
        ''' Montar o Dataframe e rodar todas as possibilidades de De->Para.

        - df_mutiplo: tabela com as informações que serão fixas no De->Para (notas,ocorrencias)

        - coluna_coord_multipla Multipla: Nome da coluna das coordenadas

        - coluna_nome_multipla: Nome da coluna com rotulo (index) dos dados

        - df_possib: tabela com as varias possibilidade de origem/Destinos

        - coluna_nome_possib: Nome da coluna com rotulo (index) dos dados

        - coluna_coord_possib: Nome da coluna das coordenadas

        - destination: True para tabela multipla com destino e false para tabela possibilidade como destino

        **Saída**: Df com todas as amostras '''

        all_distances = []
        all_durations = []
        coord_multi = df_mutiplo[coluna_coord_multipla].tolist()
        rot_multi = df_mutiplo[coluna_nome_multipla].tolist()
        coord_possib = df_possib[coluna_coord_possib].tolist()
        rot_possib = df_possib[coluna_nome_possib].tolist()

        for c, r in zip(coord_possib, rot_possib):
            print(f'\nSimulando rotas para {r}')
            for cm in coord_multi:
                if destination:
                    distancia, tempo = self.distancia_tempo(c, cm)
                else:
                    distancia, tempo = self.distancia_tempo(cm, c)
                all_distances.append(distancia)
                all_durations.append(tempo)

        rot_possib_dist, rot_possib_temp = self.criar_rotulos(rot_possib)
        distancias = np.array(all_distances).reshape(len(rot_multi), len(rot_possib_dist))
        duracao = np.array(all_durations).reshape(len(rot_multi), len(rot_possib_dist))

        print(f'\n Criando os Dataframes')
        distances_df = pd.DataFrame(distancias, index=rot_multi, columns=rot_possib_dist)
        durations_df = pd.DataFrame(duracao, index=rot_multi, columns=rot_possib_temp)

        return distances_df,durations_df
