# -*- coding: utf-8 -*-
import subprocess

if __name__ == '__main__':
    tables = ["auth_group",
              "auth_group_permissions",
              "auth_permission",
              "auth_user",
              "auth_user_groups",
              "auth_user_user_permissions",
              "fu_componente",
              "fu_componente_estados",
              "fu_componentesparque",
              "fu_configuracionfu",
              "fu_contractual",
              "fu_estadofu",
              "fu_paradas",
              "fu_paradasgrua",
              "fu_paradastrabajo",
              "fu_plan",
              "fu_registros",
              "fu_relacionesfu",
              "ncr_componente",
              "ncr_estadorevision",
              "ncr_fotos",
              "ncr_observacion",
              "ncr_observador",
              "ncr_revision",
              "ncr_severidad",
              "ncr_subcomponente",
              "ncr_tipo",
              "usuarios_general",
              "usuarios_usuario",
              "vista_aerogenerador",
              "vista_parquesolar"]

    #tables_str = ' '.join(tables)
    cmd = 'mysqldump -u root -pcntpasscfg controlobras'
    command = cmd.split() + tables
    with open('controlobras.sql', 'w') as f:
        subprocess.call(command, stdout=f)

