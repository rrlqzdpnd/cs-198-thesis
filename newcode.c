#include <stdio.h>
#include <nfc/nfc.h>
#include <nfc/nfc-types.h>
#include <nfc/utils/mifare.h>
#include <stdlib.h>
#include <string.h>

static mifare_param mp;
static nfc_device *pnd = NULL;
static nfc_context *context = NULL;
static nfc_target nt;
static nfc_modulation nm = { .nmt = NMT_ISO14443A, .nbr = NBR_106 };
static int keys[] = {
	// insert new keys here
	0x50, 0x49, 0x4e, 0x41, 0x44, 0x4f,
	0x31, 0x32, 0x31, 0x32, 0x31, 0x32,
	// these should be deleted
	0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
	0xd3, 0xf7, 0xd3, 0xf7, 0xd3, 0xf7,
	0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5,
	0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5,
	0x4d, 0x3a, 0x99, 0xc3, 0x51, 0xdd,
	0x1a, 0x98, 0x2c, 0x7e, 0x45, 0x9a,
	0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0xa0, 0xb0, 0xc0, 0xd0, 0xe0, 0xf0,
};

void print_hex(uint8_t pbtData[], int szDate) {
	int i;
	for(i=0; i<szDate; i++)
		printf("%02x ", pbtData[i]);
	printf("\n");
}

void readBlock(int start, int end) {
	int i;
	for(i=start; i<=end; i++) {
		bool res = nfc_initiator_mifare_cmd(pnd, MC_READ, i, &mp);
		if(res) {
			printf("Block %d data: ", i);
			print_hex(mp.mpd.abtData, 16);
		}
		else
			nfc_perror(pnd, "nfc_initiator_mifare_cmd");
	}
}

bool authenticate(int block, int length, char *userkey[]) {
	if(length != 6)
		return false;

	mp.mpa.abtAuthUid[0] = nt.nti.nai.abtUid[0];
	mp.mpa.abtAuthUid[1] = nt.nti.nai.abtUid[1];
	mp.mpa.abtAuthUid[2] = nt.nti.nai.abtUid[2];
	mp.mpa.abtAuthUid[3] = nt.nti.nai.abtUid[3];
	
	int i;
	for(i=0; i<9; i++) {
		nfc_initiator_select_passive_target(pnd, nm, NULL, 0, &nt);
		mp.mpa.abtKey[0] = keys[i*6+0];
		mp.mpa.abtKey[1] = keys[i*6+1];
		mp.mpa.abtKey[2] = keys[i*6+2];
		mp.mpa.abtKey[3] = keys[i*6+3];
		mp.mpa.abtKey[4] = keys[i*6+4];
		mp.mpa.abtKey[5] = keys[i*6+5];
		printf("Auth ID: %02x, %02x, %02x, %02x\n", mp.mpa.abtAuthUid[0], mp.mpa.abtAuthUid[1], mp.mpa.abtAuthUid[2], mp.mpa.abtAuthUid[3]);
		printf("Key A: %02x, %02x, %02x, %02x, %02x, %02x\n", mp.mpa.abtKey[0], mp.mpa.abtKey[1], mp.mpa.abtKey[2], mp.mpa.abtKey[3], mp.mpa.abtKey[4], mp.mpa.abtKey[5]);
		bool res1 = nfc_initiator_mifare_cmd(pnd, MC_AUTH_A, block, &mp);
		
		nfc_initiator_select_passive_target(pnd, nm, NULL, 0, &nt);
		mp.mpa.abtKey[0] = strtol(userkey[0], NULL, 16);
		mp.mpa.abtKey[1] = strtol(userkey[1], NULL, 16);
		mp.mpa.abtKey[2] = strtol(userkey[2], NULL, 16);
		mp.mpa.abtKey[3] = strtol(userkey[3], NULL, 16);
		mp.mpa.abtKey[4] = strtol(userkey[4], NULL, 16);
		mp.mpa.abtKey[5] = strtol(userkey[5], NULL, 16);
		printf("Key B: %02x, %02x, %02x, %02x, %02x, %02x\n", mp.mpa.abtKey[0], mp.mpa.abtKey[1], mp.mpa.abtKey[2], mp.mpa.abtKey[3], mp.mpa.abtKey[4], mp.mpa.abtKey[5]);
		bool res2 = nfc_initiator_mifare_cmd(pnd, MC_AUTH_B, block, &mp);
			
		if(res1 && res2)
			return true;
	
		printf("\n");
	}
	return false;
}

int main(int argc, char *argv[]) {
	nfc_init(&context);
	if(context == NULL) {
		printf("Unable to initialize libnfc\n");
		return -1;
	}
	
	pnd = nfc_open(context, NULL);
	if(pnd == NULL) {
		printf("Unable to open NFC device\n");
		nfc_exit(context);
		return -1;
	}
	
	if(nfc_initiator_init(pnd) < 0) {
		nfc_close(pnd);
		nfc_exit(context);
		return -1;
	}
	
	// Configure the NFC reader
	nfc_device_set_property_bool(pnd, NP_ACTIVATE_FIELD, false);
	nfc_device_set_property_bool(pnd, NP_INFINITE_SELECT, true);
	
	nfc_device_set_property_bool(pnd, NP_HANDLE_CRC, true);
	nfc_device_set_property_bool(pnd, NP_HANDLE_PARITY, true);
	// nfc_device_set_property_bool(pnd, NP_AUTO_ISO14443_4, false);
	
	nfc_device_set_property_bool(pnd, NP_ACTIVATE_FIELD, true);
	
	// printf("Connected to NFC Reader: %s\n", nfc_device_get_name(pnd));
	
	int sector, j;
	for(sector = 1; sector<2; sector++) {
		printf("Getting sector %d\n", sector);
		int authBlock = (sector*4)-1;
		int startBlock = authBlock - 3;
		nfc_initiator_select_passive_target(pnd, nm, NULL, 0, &nt);
		bool res = authenticate(authBlock, argc-1, argv+1);
		if(res)
			readBlock(startBlock, authBlock);
	}
	
	printf("Closing connection to NFC Reader...\n");
	nfc_close(pnd);
	nfc_exit(context);
	return 0;
}
