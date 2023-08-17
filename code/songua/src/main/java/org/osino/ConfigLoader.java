package org.osino;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;

public class ConfigLoader {
    private HashMap<String, String> content;

    public boolean containsKey(String key) {
        return this.content.containsKey(key);
    }

    public ConfigLoader(String fileName) {
        // prepare the file path
        // Path dataFolder = Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "dump");
        // Path filePath = Paths.get(dataFolder.toString(), fileName + ".json");
        Path filePath = Path.of(fileName);
        try {
            // read in the config file
            String content = Files.readString(filePath, StandardCharsets.US_ASCII);
            this.content = JSON.parseObject(content,  new TypeReference<HashMap<String, String>>(){});
        } catch (IOException e) {
            System.out.println("cannot open file " + fileName);
        }
    }

    public String get(String key) {
        return this.content.get(key);
    }

    public int getInteger(String key) {
        return Integer.parseInt(this.content.get(key));
    }

    public double getDouble(String key) {
        return Double.parseDouble(this.content.get(key));
    }

    public ArrayList<String> getStringList(String key) {
        return JSON.parseObject(this.content.get(key), new TypeReference<ArrayList<String>>(){});
    }

    public boolean getBoolean(String key) {
        return Boolean.parseBoolean(this.content.get(key));
    }

    public HashMap<String, Double> getClass(String key) {
        return  JSON.parseObject(this.content.get(key), new TypeReference<HashMap<String, Double>>(){});
    }

    public ArrayList<Integer> getIntegerList(String key) {
        return  JSON.parseObject(this.content.get(key), new TypeReference<ArrayList<Integer>>(){});
    }
}
