#include "ppm.h"

int get_ppm_files(const char *dirpath, char files[][MAX_PATH], int *count) {
    DIR *dir = opendir(dirpath);
    if (!dir) {
        fprintf(stderr, "ERROR: Cannot open directory: %s\n", dirpath);
        return -1;
    }
    struct dirent *entry;
    *count = 0;
    while ((entry = readdir(dir)) != NULL) {
        const char *name = entry->d_name;
        size_t len = strlen(name);
        if (len > 4 && strcmp(name + len - 4, ".ppm") == 0) {
            snprintf(files[*count], MAX_PATH, "%s/%s", dirpath, name);
            (*count)++;
        }
    }
    closedir(dir);
    return 0;
}

PPMImage *read_ppm(const char *filepath) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        fprintf(stderr, "ERROR: Cannot open file: %s\n", filepath);
        return NULL;
    }

    char magic[4];
    if (fscanf(fp, "%3s", magic) != 1 || strcmp(magic, "P3") != 0) {
        fprintf(stderr, "ERROR: Not a valid P3 PPM file: %s\n", filepath);
        fclose(fp);
        return NULL;
    }

    PPMImage *img = (PPMImage *)malloc(sizeof(PPMImage));
    if (!img) {
        fclose(fp);
        return NULL;
    }

    int comments = 0;
    char line_buf[4096];
    while (fgets(line_buf, sizeof(line_buf), fp)) {
        if (line_buf[0] == '#') {
            comments++;
            continue;
        }
        if (comments > 0 || line_buf[0] != '#') {
            break;
        }
    }

    fseek(fp, 0, SEEK_SET);
    fscanf(fp, "%3s", magic);

    while (1) {
        int c = fgetc(fp);
        if (c == '#') {
            while (fgetc(fp) != '\n');
        } else if (c == EOF) {
            break;
        } else if (c != ' ' && c != '\n' && c != '\t' && c != '\r') {
            ungetc(c, fp);
            break;
        }
    }

    if (fscanf(fp, "%d %d", &img->width, &img->height) != 2) {
        fprintf(stderr, "ERROR: Cannot read dimensions from: %s\n", filepath);
        free(img);
        fclose(fp);
        return NULL;
    }

    if (fscanf(fp, "%d", &img->max_val) != 1) {
        fprintf(stderr, "ERROR: Cannot read max value from: %s\n", filepath);
        free(img);
        fclose(fp);
        return NULL;
    }

    int total = img->width * img->height * 3;
    img->pixels = (unsigned char *)malloc(total);
    if (!img->pixels) {
        free(img);
        fclose(fp);
        return NULL;
    }

    int idx = 0;
    int r, g, b;
    while (idx < total && fscanf(fp, "%d %d %d", &r, &g, &b) == 3) {
        img->pixels[idx++] = (unsigned char)r;
        img->pixels[idx++] = (unsigned char)g;
        img->pixels[idx++] = (unsigned char)b;
    }

    fclose(fp);
    return img;
}

void write_ppm(const char *filepath, const PPMImage *img) {
    FILE *fp = fopen(filepath, "w");
    if (!fp) {
        fprintf(stderr, "ERROR: Cannot write file: %s\n", filepath);
        return;
    }
    fprintf(fp, "P3\n%d %d\n%d\n", img->width, img->height, img->max_val);
    int total = img->width * img->height * 3;
    for (int i = 0; i < total; i += 3) {
        fprintf(fp, "%d %d %d\n", img->pixels[i], img->pixels[i+1], img->pixels[i+2]);
    }
    fclose(fp);
}

void free_ppm(PPMImage *img) {
    if (img) {
        free(img->pixels);
        free(img);
    }
}
