/*==============================================================*/
/* DBMS name:      MySQL 4.0                                    */
/* Created on:     29/05/2021 13:38:00                          */
/*==============================================================*/


drop index TERDAPAT_FK on HARGA;

drop index MEMILIKI_FK on HARGA;

drop table if exists HARGA;

drop table if exists KOMODITAS;

drop table if exists WILAYAH;

/*==============================================================*/
/* Table: HARGA                                                 */
/*==============================================================*/
create table HARGA
(
   ID_HARGA                       int                            not null,
   ID_WILAYAH                     int                            not null,
   ID_KOMODITAS                   int                            not null,
   HARGA                          int,
   TANGGAL                        date,
   primary key (ID_HARGA)
)
type = InnoDB;

/*==============================================================*/
/* Index: MEMILIKI_FK                                           */
/*==============================================================*/
create index MEMILIKI_FK on HARGA
(
   ID_KOMODITAS
);

/*==============================================================*/
/* Index: TERDAPAT_FK                                           */
/*==============================================================*/
create index TERDAPAT_FK on HARGA
(
   ID_WILAYAH
);

/*==============================================================*/
/* Table: KOMODITAS                                             */
/*==============================================================*/
create table KOMODITAS
(
   ID_KOMODITAS                   int                            not null,
   NAMA_KOMODITAS                 varchar(50),
   ID_FOREIGN                     int,
   primary key (ID_KOMODITAS)
)
type = InnoDB;

/*==============================================================*/
/* Table: WILAYAH                                               */
/*==============================================================*/
create table WILAYAH
(
   ID_WILAYAH                     int                            not null,
   NAMA_WILAYAH                   varchar(50),
   ID_FOREIGN_WILAYAH             int,
   primary key (ID_WILAYAH)
)
type = InnoDB;

alter table HARGA add constraint FK_MEMILIKI foreign key (ID_KOMODITAS)
      references KOMODITAS (ID_KOMODITAS) on delete restrict on update restrict;

alter table HARGA add constraint FK_TERDAPAT foreign key (ID_WILAYAH)
      references WILAYAH (ID_WILAYAH) on delete restrict on update restrict;

